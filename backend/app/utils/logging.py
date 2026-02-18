"""Centralized logging configuration for the application."""

import logging
import queue
import sys
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.config.settings import settings

_loggers = {}
# Create a boundless queue
log_queue = queue.Queue(-1)
queue_listener: Optional[QueueListener] = None


def get_formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _setup_queue_listener():
    """Initialize and start the QueueListener with actual handlers."""
    global queue_listener
    if queue_listener is None:
        formatter = get_formatter()

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        console_handler.setFormatter(formatter)

        # File Handler
        log_file = Path("logs/app.log")
        log_file.parent.mkdir(
            exist_ok=True
        )  # Create logs directory if it doesn't exist
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        file_handler.setFormatter(formatter)

        # Queue Listener (runs on separate thread)
        queue_listener = QueueListener(
            log_queue, console_handler, file_handler, respect_handler_level=True
        )
        queue_listener.start()


def close_logging():
    """Stop the queue listener to ensure all logs are flushed."""
    global queue_listener
    if queue_listener:
        queue_listener.stop()
        queue_listener = None


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the given name.

    Args:
        name: Name of the logger (typically __name__ from the calling module)

    Returns:
        Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)

    if logger.handlers:
        _loggers[name] = logger
        return logger

    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    logger.propagate = False

    # Use QueueHandler to send logs to the background listener
    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)

    _loggers[name] = logger
    return logger


def init_logging():
    """Initialize the logging system."""
    _setup_queue_listener()

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    if not root_logger.handlers:
        queue_handler = QueueHandler(log_queue)
        root_logger.addHandler(queue_handler)
