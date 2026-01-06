"""Logging utilities for the hybrid architecture."""
from __future__ import annotations

import logging

DEFAULT_LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: int = DEFAULT_LOG_LEVEL) -> None:
    """Configure the root logger for the package if it has not been set.

    The configuration is idempotent so importing modules will not spam the
    output with duplicate handlers during testing.
    """
    if not logging.getLogger().handlers:
        logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def get_logger(name: str = "FAR-Hybrid") -> logging.Logger:
    """Return a namespaced logger configured for the hybrid stack."""
    configure_logging()
    return logging.getLogger(name)
