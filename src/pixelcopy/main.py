"""PixelCopy process entry point."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Sequence

from PySide6.QtCore import QTimer

from pixelcopy.app import ApplicationController, create_application
from pixelcopy.config.paths import AppPaths
from pixelcopy.config.settings import SettingsStore
from pixelcopy.database.connection import connect_database
from pixelcopy.database.repositories import HistoryRepository
from pixelcopy.database.schema import migrate
from pixelcopy.utils.logging import configure_logging


def main(arguments: Sequence[str] | None = None) -> int:
    """Initialize platform services and enter the Qt event loop."""
    process_arguments = list(arguments) if arguments is not None else list(sys.argv)
    ocr_smoke_test = "--smoke-test-ocr" in process_arguments
    smoke_test = "--smoke-test" in process_arguments or ocr_smoke_test
    private_arguments = {"--smoke-test", "--smoke-test-ocr"}
    qt_arguments = [argument for argument in process_arguments if argument not in private_arguments]
    if ocr_smoke_test:
        importlib.import_module("paddle")
        importlib.import_module("paddleocr")
    paths = AppPaths.discover()
    paths.ensure_directories()
    logger = configure_logging(paths.log_dir)
    logger.info("PixelCopy starting")

    app = create_application(qt_arguments)
    settings_store = SettingsStore(paths.config_dir / "settings.json", logger)
    history_connection = connect_database(paths.data_dir / "history.sqlite3")
    migrate(history_connection)
    history_repository = HistoryRepository(history_connection, paths.data_dir / "thumbnails")
    controller = ApplicationController(app, settings_store, history_repository=history_repository)
    controller.start()
    if smoke_test:
        QTimer.singleShot(250, app.quit)
    else:
        controller.enable_global_shortcut()
    return app.exec()
