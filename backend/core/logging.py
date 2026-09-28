import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.config import settings

# Context variable for request correlation ID
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class JSONLogFormatter(logging.Formatter):
    """
    Format logs as JSON objects for centralized log aggregators (e.g., Datadog, CloudWatch).
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
            "correlation_id": correlation_id_ctx.get(),
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_obj["extra"] = record.extra

        return json.dumps(log_obj)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Format logs with ANSI colors for readable local terminal development.
    """

    COLORS = {
        logging.DEBUG: "\033[36m",    # Cyan
        logging.INFO: "\033[32m",     # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",    # Red
        logging.CRITICAL: "\033[35m", # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        cid = correlation_id_ctx.get()
        cid_str = f" [{cid[:8]}]" if cid else ""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        msg = f"{color}[{timestamp}] [{record.levelname:<7}]{self.RESET}{cid_str} {record.name}: {record.getMessage()}"
        if record.exc_info:
            msg += "\n" + self.formatException(record.exc_info)
        return msg


def setup_logging() -> None:
    """
    Initialize root and application loggers based on settings.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_FORMAT == "json" or settings.is_production:
        stream_handler.setFormatter(JSONLogFormatter())
    else:
        stream_handler.setFormatter(ColoredConsoleFormatter())

    root_logger.addHandler(stream_handler)

    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DATABASE_ECHO else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
