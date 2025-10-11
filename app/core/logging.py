import json
import logging
import os
from typing import Any

from app.middleware.logging import RequestIdLogFilter


class JsonFormatter(logging.Formatter):
    DEFAULT_KEYS = {
        "level": "level",
        "logger": "logger",
        "message": "msg",
        "time": "asctime",
        "module": "module",
        "funcName": "func",
        "lineno": "line",
        "request_id": "request_id",
        "user_id": "user_id",
    }

    def format(self, record: logging.LogRecord) -> str:
        base = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "asctime": self.formatTime(record, self.datefmt),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        # extra をすべてJSONに落とす
        # record.__dict__ から「既知の属性」を除いたものが extra 相当
        known = set(vars(logging.makeLogRecord({})).keys())
        data: dict[str, Any] = {}
        for k, v in record.__dict__.items():
            if k not in known and not k.startswith("_"):
                # pydanticのValidationErrorなどでシリアライズ失敗を避ける
                try:
                    json.dumps(v)
                    data[k] = v
                except Exception:
                    data[k] = str(v)

        base.update(data)
        return json.dumps(base, ensure_ascii=False)


def setup_logging() -> None:
    # ルートロガーをJSONに統一
    root = logging.getLogger()
    root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

    # 既存ハンドラをクリア（uvicorn等が先に設定している場合を上書き）
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)

    # リクエストID／ユーザIDを全ログに付与
    root.addFilter(RequestIdLogFilter())

    # よく使うロガーのレベル
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)  # SQLログもrequest_id付与される
    logging.getLogger("app").setLevel(logging.INFO)
