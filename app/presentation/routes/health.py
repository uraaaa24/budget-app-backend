from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

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
