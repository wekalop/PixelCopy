"""Qt application construction."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from dataclasses import replace

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QApplication

from pixelcopy.config.constants import APP_NAME, APP_ORGANIZATION, APP_VERSION
from pixelcopy.config.settings import ApplicationSettings, SettingsStore
from pixelcopy.controllers.capture_controller import CaptureController
from pixelcopy.controllers.image_import_controller import ImageImportController
from pixelcopy.controllers.ocr_controller import OCRController
from pixelcopy.controllers.preprocessing_controller import PreprocessingController
from pixelcopy.ocr.base_engine import OCREngine
from pixelcopy.ocr.paddle_engine import PaddleOCREngine
from pixelcopy.preprocessing.pipeline import PreprocessingPipeline
from pixelcopy.services.image_import_service import ImageImportService
from pixelcopy.services.ocr_service import OCRService
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

    def __init__(
        self,
        application: QApplication,
        settings_store: SettingsStore,
        ocr_engine: OCREngine | None = None,
    ) -> None:
        super().__init__()
        self._application = application
        self._settings_store = settings_store
        self._settings = settings_store.load()
        apply_theme(application, Theme(self._settings.theme))
        self.window = MainWindow(self._settings.theme, self._settings.global_shortcut)
        self.image_import_controller = ImageImportController(
            application,
            self.window.extract_page,
            ImageImportService(),
        )
        self.ocr_controller = OCRController(
            application,
            self.window.extract_page,
            OCRService(ocr_engine or PaddleOCREngine()),
        )
        self.preprocessing_controller = PreprocessingController(
            self.window.extract_page,
            PreprocessingPipeline(),
        )
        self.image_import_controller.document_imported.connect(self.ocr_controller.set_document)
        self.image_import_controller.document_imported.connect(
            self.preprocessing_controller.set_document
        )
        self.image_import_controller.document_cleared.connect(self.ocr_controller.clear_document)
        self.image_import_controller.document_cleared.connect(
            self.preprocessing_controller.clear_document
        )
        self.preprocessing_controller.document_processed.connect(self.ocr_controller.set_document)
        self.preprocessing_controller.original_restored.connect(self.ocr_controller.set_document)
        self.capture_controller = CaptureController(
            application,
            self.window.extract_page,
            self.image_import_controller,
        )
        application.aboutToQuit.connect(self.capture_controller.close)
        self.window.settings_page.theme_changed.connect(self.change_theme)
        self.window.settings_page.shortcut_changed.connect(self.change_shortcut)

    def start(self) -> None:
        """Show the main application window."""
        self.window.show()

    def enable_global_shortcut(self) -> None:
        """Register the configured Windows screen-capture shortcut."""
        self.capture_controller.register_shortcut(self._settings.global_shortcut)

    def change_shortcut(self, value: str) -> None:
        """Register and persist a valid conflict-free capture shortcut."""
        if not value or value == self._settings.global_shortcut:
            return
        if not self.capture_controller.register_shortcut(value):
            self.window.settings_page.shortcut_editor.setText(self._settings.global_shortcut)
            return
        updated = replace(self._settings, global_shortcut=value)
        self._settings_store.save(updated)
        self._settings = updated

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
