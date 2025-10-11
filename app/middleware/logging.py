from __future__ import annotations

import contextvars
import json
import logging
import time
import uuid
from typing import Any
from urllib.parse import parse_qsl, urlencode

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("app.middleware")

# ===== Context =====
request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
user_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "user_id", default=None
)  # 使いたければ依存でセット

# ===== Config =====
SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "x-auth-token"}
SENSITIVE_QUERY_KEYS = {
    "access_token",
    "token",
    "id_token",
    "code",
    "password",
    "apikey",
    "api_key",
}
BINARY_CT_PREFIXES = (
    "image/",
    "audio/",
    "video/",
    "application/zip",
    "application/octet-stream",
    "application/pdf",
)
HEALTH_PATHS = {"/health", "/healthz", "/ready", "/live"}
SLOW_THRESHOLD_S = 1.0  # ここを好みで


def _redact_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k: ("***" if k.lower() in SENSITIVE_HEADERS else v) for k, v in headers.items()}


def _redact_query(query: str) -> str:
    if not query:
        return ""
    pairs = []
    for k, v in parse_qsl(query, keep_blank_values=True):
        pairs.append((k, "***" if k.lower() in SENSITIVE_QUERY_KEYS else v))
    return urlencode(pairs)


def _add_header(
    headers: list[tuple[bytes, bytes]], key: bytes, value: bytes
) -> list[tuple[bytes, bytes]]:
    lowered = key.lower()
    out = [(k, v) for (k, v) in headers if k.lower() != lowered]
    out.append((key, value))
    return out


def _safe_preview(b: bytes, limit: int, content_type: str | None) -> str:
    if not b:
        return ""
    if content_type and any(content_type.startswith(p) for p in BINARY_CT_PREFIXES):
        return f"<{min(len(b), limit)} bytes, binary>"
    # JSONなら軽く整形
    if content_type and content_type.startswith("application/json"):
        try:
            obj = json.loads(b[:limit].decode("utf-8"))
            return json.dumps(obj, ensure_ascii=False)[:limit]
        except Exception:
            pass
    try:
        return b[:limit].decode("utf-8")
    except UnicodeDecodeError:
        return f"<{min(len(b), limit)} bytes, binary>"


class RequestIdLogFilter(logging.Filter):
    """全ログに request_id / user_id を付けるための Filter"""

    def filter(self, record: logging.LogRecord) -> bool:
        rid = request_id_ctx.get()
        uid = user_id_ctx.get()
        # 既に付与済みなら上書きしない
        if not hasattr(record, "request_id"):
            record.request_id = rid
        if not hasattr(record, "user_id"):
            record.user_id = uid
        return True


# アプリ起動時にどこかで:
# logging.getLogger().addFilter(RequestIdLogFilter())


class RequestLoggingMiddleware:
    """ASGI middleware that logs request/response with context and captures exceptions."""

    def __init__(self, app: ASGIApp, *, max_body_preview: int = 4096):
        self.app = app
        self.max_body_preview = max_body_preview

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> Any:
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        start = time.perf_counter()
        request_id, token = self._set_request_id(scope)
        ctx = self._extract_request_context(scope, request_id)

        req_preview, req_len, receive_wrapper = self._make_receive_wrapper(receive)
        resp_state, send_wrapper = self._make_send_wrapper(send, request_id)

        try:
            await self.app(scope, receive_wrapper, send_wrapper)
        except Exception:
            self._log_error(ctx, req_preview, req_len, start)
            raise
        else:
            self._log_success(ctx, req_preview, req_len, resp_state, start)
        finally:
            request_id_ctx.reset(token)

    # ----------------- helpers -----------------

    def _set_request_id(self, scope: Scope) -> tuple[str, contextvars.Token]:
        raw_headers = scope.get("headers", [])
        headers = {k.decode().lower(): v.decode() for k, v in raw_headers}
        request_id = headers.get("x-request-id") or str(uuid.uuid4())
        token = request_id_ctx.set(request_id)
        return request_id, token

    def _extract_request_context(self, scope: Scope, request_id: str) -> dict[str, Any]:
        raw_headers = scope.get("headers", [])
        headers = {k.decode().lower(): v.decode() for k, v in raw_headers}
        query_raw = (scope.get("query_string") or b"").decode()
        return {
            "request_id": request_id,
            "method": scope.get("method", "-"),
            "path": scope.get("path", "-"),
            "query": _redact_query(query_raw),
            "ip": (scope.get("client") or ("-",))[0],
            "headers": _redact_headers(headers),
            "req_ct": headers.get("content-type"),
            "http_version": scope.get("http_version", ""),
            "scheme": scope.get("scheme", ""),
            "host": headers.get("host", ""),
            "path_params": scope.get("path_params") or {},
        }

    def _make_receive_wrapper(self, receive: Receive):
        req_preview = bytearray()
        total_len = 0

        async def wrapper() -> Message:
            nonlocal total_len
            message = await receive()
            if message["type"] == "http.request":
                body: bytes = message.get("body", b"") or b""
                total_len += len(body)
                if body and len(req_preview) < self.max_body_preview:
                    remain = self.max_body_preview - len(req_preview)
                    if remain > 0:
                        req_preview.extend(body[:remain])
            return message

        return req_preview, lambda: total_len, wrapper

    def _make_send_wrapper(self, send: Send, request_id: str):
        state: dict[str, Any] = {
            "status_code": 0,
            "resp_preview": bytearray(),
            "resp_ct": None,
            "headers": [],
            "resp_len": 0,
        }

        async def wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                state["status_code"] = message["status"]
                state["headers"] = message.get("headers", [])
                # Content-Type
                for k, v in state["headers"]:
                    if k.lower() == b"content-type":
                        try:
                            state["resp_ct"] = v.decode()
                        except Exception:
                            state["resp_ct"] = None
                # X-Request-ID を必ず返す
                message["headers"] = _add_header(
                    state["headers"], b"x-request-id", request_id.encode()
                )

            elif message["type"] == "http.response.body":
                body: bytes = message.get("body", b"") or b""
                state["resp_len"] += len(body)
                if body and len(state["resp_preview"]) < self.max_body_preview:
                    remain = self.max_body_preview - len(state["resp_preview"])
                    if remain > 0:
                        state["resp_preview"].extend(body[:remain])

            await send(message)

        return state, wrapper

    def _log_error(
        self, ctx: dict[str, Any], req_preview: bytearray, req_len_fn, start: float
    ) -> None:
        elapsed = time.perf_counter() - start
        logger.exception(
            "REQUEST ERROR",
            extra={
                "request_id": ctx["request_id"],
                "method": ctx["method"],
                "path": ctx["path"],
                "query": ctx["query"],
                "ip": ctx["ip"],
                "elapsed_s": round(elapsed, 3),
                "http_version": ctx["http_version"],
                "scheme": ctx["scheme"],
                "host": ctx["host"],
                "path_params": ctx["path_params"],
                "headers": ctx["headers"],
                "req_ct": ctx["req_ct"],
                "req_len": req_len_fn(),
                "req_body_preview": _safe_preview(
                    bytes(req_preview), self.max_body_preview, ctx["req_ct"]
                ),
            },
        )

    def _log_success(
        self,
        ctx: dict[str, Any],
        req_preview: bytearray,
        req_len_fn,
        state: dict[str, Any],
        start: float,
    ) -> None:
        elapsed = time.perf_counter() - start
        status = int(state["status_code"])
        emoji = "✅" if status < 300 else "🔄" if status < 400 else "⚠️" if status < 500 else "❌"
        is_slow = elapsed >= SLOW_THRESHOLD_S
        log_fn = (
            logger.warning
            if (status >= 400 or is_slow) and status < 500
            else (logger.error if status >= 500 else logger.info)
        )

        # Content-Length をヘッダから拾う（ない場合は蓄積値）
        hdrs = {k.decode().lower(): v.decode() for k, v in state.get("headers", [])}
        resp_len_hdr = hdrs.get("content-length")
        resp_len = (
            int(resp_len_hdr) if resp_len_hdr and resp_len_hdr.isdigit() else state["resp_len"]
        )

        payload: dict[str, Any] = {
            "request_id": ctx["request_id"],
            "method": ctx["method"],
            "path": ctx["path"],
            "query": ctx["query"],
            "ip": ctx["ip"],
            "status": status,
            "elapsed_s": round(elapsed, 3),
            "slow": is_slow,
            "http_version": ctx["http_version"],
            "scheme": ctx["scheme"],
            "host": ctx["host"],
            "path_params": ctx["path_params"],
            "req_ct": ctx["req_ct"],
            "req_len": req_len_fn(),
            "resp_ct": state["resp_ct"],
            "resp_len": resp_len,
        }

        is_health_ok = ctx["path"] in HEALTH_PATHS and status < 400
        if (status >= 400 or is_slow) and not is_health_ok:
            payload["headers"] = ctx["headers"]
            payload["resp_headers"] = _redact_headers(hdrs)
            payload["req_body_preview"] = _safe_preview(
                bytes(req_preview), self.max_body_preview, ctx["req_ct"]
            )
            payload["resp_body_preview"] = _safe_preview(
                bytes(state["resp_preview"]), self.max_body_preview, state["resp_ct"]
            )

        log_fn(
            f"{emoji} {ctx['method']} {ctx['path']}{('?' + ctx['query']) if ctx['query'] else ''} "
            f"→ {status} ({elapsed:.3f}s){' SLOW' if is_slow else ''} ip={ctx['ip']}",
            extra=payload
            if not is_health_ok
            else {"status": status, "elapsed_s": payload["elapsed_s"]},
        )
