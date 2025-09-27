from __future__ import annotations

import contextvars
import logging
import time
import uuid
from typing import Any

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("app.middleware")

# Request-ID を他所へ伝播するための ContextVar
request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)

# 機微ヘッダ（ログでは値をマスク）
SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "x-auth-token"}

# バイナリ扱いする Content-Type プレフィックス
BINARY_CT_PREFIXES = (
    "image/",
    "audio/",
    "video/",
    "application/zip",
    "application/octet-stream",
    "application/pdf",
)

# ノイズ抑制したいヘルスパス
HEALTH_PATHS = {"/health", "/healthz", "/ready", "/live"}


def _redact_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k: ("***" if k.lower() in SENSITIVE_HEADERS else v) for k, v in headers.items()}


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
    try:
        return b[:limit].decode("utf-8")
    except UnicodeDecodeError:
        return f"<{min(len(b), limit)} bytes, binary>"


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

        req_preview, receive_wrapper = self._make_receive_wrapper(receive)
        resp_state, send_wrapper = self._make_send_wrapper(send, request_id)

        try:
            await self.app(scope, receive_wrapper, send_wrapper)
        except Exception:
            self._log_error(ctx, req_preview, start)
            raise
        else:
            self._log_success(ctx, req_preview, resp_state, start)
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
        return {
            "request_id": request_id,
            "method": scope.get("method", "-"),
            "path": scope.get("path", "-"),
            "query": (scope.get("query_string") or b"").decode(),
            "ip": (scope.get("client") or ("-",))[0],
            "headers": _redact_headers(headers),
            "req_ct": headers.get("content-type"),
        }

    def _make_receive_wrapper(self, receive: Receive):
        req_preview = bytearray()

        async def wrapper() -> Message:
            message = await receive()
            if message["type"] == "http.request":
                body: bytes = message.get("body", b"") or b""
                if body and len(req_preview) < self.max_body_preview:
                    remain = self.max_body_preview - len(req_preview)
                    if remain > 0:
                        req_preview.extend(body[:remain])
            return message

        return req_preview, wrapper

    def _make_send_wrapper(self, send: Send, request_id: str):
        state: dict[str, Any] = {
            "status_code": 0,
            "resp_preview": bytearray(),
            "resp_ct": None,
            "headers": [],
        }

        async def wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                state["status_code"] = message["status"]
                state["headers"] = message.get("headers", [])
                # Content-Type を拾う
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
                if body and len(state["resp_preview"]) < self.max_body_preview:
                    remain = self.max_body_preview - len(state["resp_preview"])
                    if remain > 0:
                        state["resp_preview"].extend(body[:remain])

            await send(message)

        return state, wrapper

    def _log_error(self, ctx: dict[str, Any], req_preview: bytearray, start: float) -> None:
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
                "headers": ctx["headers"],
                "req_body_preview": _safe_preview(
                    bytes(req_preview), self.max_body_preview, ctx["req_ct"]
                ),
            },
        )

    def _log_success(
        self, ctx: dict[str, Any], req_preview: bytearray, state: dict[str, Any], start: float
    ) -> None:
        elapsed = time.perf_counter() - start
        status = int(state["status_code"])
        emoji = "✅" if status < 300 else "🔄" if status < 400 else "⚠️" if status < 500 else "❌"
        log_fn = logger.info if status < 400 else (logger.warning if status < 500 else logger.error)

        payload: dict[str, Any] = {
            "request_id": ctx["request_id"],
            "method": ctx["method"],
            "path": ctx["path"],
            "query": ctx["query"],
            "ip": ctx["ip"],
            "status": status,
            "elapsed_s": round(elapsed, 3),
        }

        # ヘルスパスは 2xx なら詳細抑制
        is_health_ok = ctx["path"] in HEALTH_PATHS and status < 400
        if status >= 400 and not is_health_ok:
            payload["headers"] = ctx["headers"]
            payload["req_body_preview"] = _safe_preview(
                bytes(req_preview), self.max_body_preview, ctx["req_ct"]
            )
            payload["resp_body_preview"] = _safe_preview(
                bytes(state["resp_preview"]), self.max_body_preview, state["resp_ct"]
            )

        log_fn(
            f"{emoji} {ctx['method']} {ctx['path']}{('?' + ctx['query']) if ctx['query'] else ''} "
            f"→ {status} ({elapsed:.3f}s) ip={ctx['ip']}",
            extra=payload
            if not is_health_ok
            else {"status": status, "elapsed_s": payload["elapsed_s"]},
        )
