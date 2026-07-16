"""PixelCopy process entry point."""

from __future__ import annotations

from collections.abc import Sequence

from pixelcopy.app import create_application
from pixelcopy.config.paths import AppPaths
from pixelcopy.ui.main_window import MainWindow
from pixelcopy.ui.styles.theme import Theme, apply_theme
from pixelcopy.utils.logging import configure_logging


def main(arguments: Sequence[str] | None = None) -> int:
    """Initialize platform services and enter the Qt event loop."""
    paths = AppPaths.discover()
    paths.ensure_directories()
    logger = configure_logging(paths.log_dir)
    logger.info("PixelCopy starting")

    app = create_application(arguments)
    apply_theme(app, Theme.LIGHT)
    window = MainWindow()
    window.show()
    return app.exec()
