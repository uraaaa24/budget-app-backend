import re
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.database import db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "ok"}


@router.get("/health/db")
async def db_health_check():
    """Check if the database is reachable"""
    try:
        ok = await run_in_threadpool(db.ping)
        if not ok:
            raise HTTPException(status_code=503, detail="Database connection failed")
        return {"status": "ok", "database": {"status": "ok"}}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}") from e


@router.get("/health/db/info")
async def db_info():
    """データベース接続情報を返す（デバッグ用）"""
    import os

    try:
        # URLをパース
        parsed = urlparse(settings.DATABASE_URL)

        # パスワードをマスク
        masked_url = re.sub(
            r'://([^:]+):([^@]+)@',
            r'://\1:****@',
            settings.DATABASE_URL
        )

        return {
            "app_env": os.getenv("APP_ENV", "not set"),
            "debug": settings.DEBUG,
            "database_url": masked_url,
            "host": parsed.hostname,
            "port": parsed.port,
            "database": parsed.path.lstrip('/') if parsed.path else None,
            "username": parsed.username,
            "scheme": parsed.scheme,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to parse database URL: {str(e)}"
        ) from e
