from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import db
from app.core.logging import setup_logging
from app.middleware import RequestLoggingMiddleware
from app.presentation.routes import health_router


def register_app() -> FastAPI:
    """Register the FastAPI application with middleware and routes."""
  
    setup_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        db.dispose() 

    app = FastAPI(
        title="Budget App API",
        description="Personal budget management application",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(health_router)
    return app
