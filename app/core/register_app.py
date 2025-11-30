import logging
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import db
from app.core.logging import setup_logging
from app.middleware import RequestLoggingMiddleware
from app.presentation.routes import (
    category_router,
    dashboard_router,
    health_router,
    transaction_router,
)

logger = logging.getLogger(__name__)


def register_app() -> FastAPI:
    """Register the FastAPI application with middleware and routes."""

    setup_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # データベースURLをログ出力（パスワードを隠す）
        masked_url = re.sub(
            r'://([^:]+):([^@]+)@',
            r'://\1:****@',
            settings.DATABASE_URL
        )
        logger.info(f"Starting application with DATABASE_URL: {masked_url}")
        logger.info(f"Database connection test: {'OK' if db.ping() else 'FAILED'}")

        yield
        db.dispose()

    app = FastAPI(
        title="Budget App API",
        description="Personal budget management application",
        version="1.0.0",
        lifespan=lifespan,
    )

    origins = ["http://localhost:3000", "https://budget-app-frontend-mu.vercel.app"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add validation error handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        print(f"DEBUG: Validation error: {exc}")
        print(f"DEBUG: Request body: {await request.body()}")
        return JSONResponse(status_code=422, content={"detail": exc.errors(), "body": exc.body})

    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(health_router)
    app.include_router(transaction_router)
    app.include_router(category_router)
    app.include_router(dashboard_router)  # Add dashboard router

    return app
