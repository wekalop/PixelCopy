"""Qt application construction."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from dataclasses import replace

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QApplication

from pixelcopy.config.constants import APP_NAME, APP_ORGANIZATION, APP_VERSION
from pixelcopy.config.settings import ApplicationSettings, SettingsStore
from pixelcopy.controllers.image_import_controller import ImageImportController
from pixelcopy.services.image_import_service import ImageImportService
from pixelcopy.ui.main_window import MainWindow
from pixelcopy.ui.styles.theme import Theme, apply_theme


def create_application(arguments: Sequence[str] | None = None) -> QApplication:
    """Create or return the process-wide Qt application."""
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing

    app = QApplication(list(arguments) if arguments is not None else sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORGANIZATION)
    app.setApplicationVersion(APP_VERSION)
    app.setStyle("Fusion")
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
    return app


class ApplicationController(QObject):
    """Coordinate settings persistence and presentation-level application state."""

    def __init__(self, application: QApplication, settings_store: SettingsStore) -> None:
        super().__init__()
        self._application = application
        self._settings_store = settings_store
        self._settings = settings_store.load()
        apply_theme(application, Theme(self._settings.theme))
        self.window = MainWindow(self._settings.theme)
        self.image_import_controller = ImageImportController(
            application,
            self.window.extract_page,
            ImageImportService(),
        )
        self.window.settings_page.theme_changed.connect(self.change_theme)

    def start(self) -> None:
        """Show the main application window."""
        self.window.show()

    def change_theme(self, value: str) -> None:
        """Validate, apply, and persist a user-selected theme."""
        try:
            theme = Theme(value)
        except ValueError:
            return
        updated = replace(self._settings, theme=theme.value)
        self._settings_store.save(updated)
        self._settings = updated
        apply_theme(self._application, theme)

    @property
    def settings(self) -> ApplicationSettings:
        """Expose the current immutable settings snapshot."""
        return self._settings
