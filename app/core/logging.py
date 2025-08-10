import logging
import sys

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Setup logging configuration"""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    if settings.DEBUG:
        log_format = "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d: %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )

    _suppress_noisy_loggers()

    _configure_sqlalchemy_logging()

    logger = logging.getLogger("app")
    logger.info(f"🚀 Starting {settings.APP_NAME} (Debug: {settings.DEBUG})")

    return logger


def _suppress_noisy_loggers():
    """Suppress noisy loggers that clutter the output"""
    noisy_loggers = [
        "uvicorn.access",
        "asyncio",
        "urllib3.connectionpool",
        "httpx",
    ]

    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def _configure_sqlalchemy_logging():
    """Configure SQLAlchemy logging based on debug mode"""
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")

    if settings.DEBUG:
        sqlalchemy_logger.setLevel(logging.INFO)
    else:
        sqlalchemy_logger.setLevel(logging.ERROR)
