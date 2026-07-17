"""Screen capture and global shortcut coordination."""

from __future__ import annotations

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from pixelcopy.controllers.image_import_controller import ImageImportController
from pixelcopy.services.global_shortcut import ShortcutRegistrationError, WindowsGlobalShortcut
from pixelcopy.services.screenshot_service import ScreenshotService
from pixelcopy.ui.overlays.screen_capture import ScreenCaptureOverlay
from pixelcopy.ui.pages.extract import ExtractPage


class CaptureController(QObject):
    """Open the selection overlay and route captures into image import."""

    def __init__(
        self,
        application: QApplication,
        page: ExtractPage,
        image_import: ImageImportController,
    ) -> None:
        super().__init__(page)
        self._page = page
        self._image_import = image_import
        self._overlay = ScreenCaptureOverlay(ScreenshotService())
        self._shortcut = WindowsGlobalShortcut(page)
        self._last_shortcut_error: str | None = None
        page.capture_requested.connect(self.begin_capture)
        self._shortcut.activated.connect(self.begin_capture)
        self._overlay.captured.connect(self._captured)

    def register_shortcut(self, shortcut: str) -> bool:
        """Register a configured shortcut or show a conflict error."""
        try:
            self._shortcut.register(shortcut)
        except ShortcutRegistrationError as error:
            self._last_shortcut_error = str(error)
            self._page.display_error(str(error))
            return False
        self._last_shortcut_error = None
        return True

    @property
    def shortcut_active(self) -> bool:
        """Return whether the configured capture hotkey is registered with Windows."""
        return self._shortcut.is_registered

    @property
    def last_shortcut_error(self) -> str | None:
        """Return the latest registration error for presentation in Settings."""
        return self._last_shortcut_error

    def close(self) -> None:
        self._shortcut.close()
        self._overlay.close()

    @Slot()
    def begin_capture(self) -> None:
        self._overlay.begin()

    @Slot(object)
    def _captured(self, value: object) -> None:
        if isinstance(value, QImage):
            self._image_import.import_qimage(value, "Screen capture")
            window = self._page.window()
            if window.isMinimized():
                window.showNormal()
            else:
                window.show()
            window.raise_()
            window.activateWindow()
