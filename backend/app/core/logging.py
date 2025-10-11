# Logging configuration
import structlog
import logging
from typing import Any, Dict
from .config import settings


def configure_logging():
    """Configure structured logging"""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=open("app.log", "w") if not settings.debug else None,
        level=logging.INFO if not settings.debug else logging.DEBUG,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger"""
    return structlog.get_logger(name)

