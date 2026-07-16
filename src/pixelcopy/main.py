"""PixelCopy process entry point."""

from __future__ import annotations

from collections.abc import Sequence

from pixelcopy.app import ApplicationController, create_application
from pixelcopy.config.paths import AppPaths
from pixelcopy.config.settings import SettingsStore
from pixelcopy.database.connection import connect_database
from pixelcopy.database.repositories import HistoryRepository
from pixelcopy.database.schema import migrate
from pixelcopy.utils.logging import configure_logging


def main(arguments: Sequence[str] | None = None) -> int:
    """Initialize platform services and enter the Qt event loop."""
    paths = AppPaths.discover()
    paths.ensure_directories()
    logger = configure_logging(paths.log_dir)
    logger.info("PixelCopy starting")

    app = create_application(arguments)
    settings_store = SettingsStore(paths.config_dir / "settings.json", logger)
    history_connection = connect_database(paths.data_dir / "history.sqlite3")
    migrate(history_connection)
    history_repository = HistoryRepository(history_connection, paths.data_dir / "thumbnails")
    controller = ApplicationController(app, settings_store, history_repository=history_repository)
    controller.start()
    controller.enable_global_shortcut()
    return app.exec()
