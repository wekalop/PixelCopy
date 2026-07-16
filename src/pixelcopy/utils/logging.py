"""Privacy-conscious application logging."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(log_dir: Path, level: int = logging.INFO) -> logging.Logger:
    """Configure rotating technical logs without recording document content."""
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("pixelcopy")
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = RotatingFileHandler(
            log_dir / "pixelcopy.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)

    return logger
