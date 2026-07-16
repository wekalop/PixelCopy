from __future__ import annotations

import logging
from pathlib import Path

from pixelcopy.utils.logging import configure_logging


def test_configure_logging_creates_rotating_log_file(tmp_path: Path) -> None:
    logger = configure_logging(tmp_path, logging.DEBUG)
    logger.info("application initialized")
    for handler in logger.handlers:
        handler.flush()

    assert (
        (tmp_path / "pixelcopy.log")
        .read_text(encoding="utf-8")
        .endswith("pixelcopy: application initialized\n")
    )
