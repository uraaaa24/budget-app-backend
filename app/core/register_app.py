from fastapi import FastAPI

from app.core.logging import setup_logging
from app.middleware import RequestLoggingMiddleware
from app.presentation.routes import health_router


def register_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    setup_logging()

    app = FastAPI(
        title="Budget App API",
        description="Personal budget management application",
        version="1.0.0",
    )

    app.add_middleware(RequestLoggingMiddleware)

    # Router for health check endpoints
    app.include_router(health_router)

    return app
