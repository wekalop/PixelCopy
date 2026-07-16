"""Image import workflow coordination."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from PySide6.QtCore import QBuffer, QIODevice, QObject, Signal
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from pixelcopy.domain.exceptions import ImageImportError
from pixelcopy.services.image_import_service import ImageImportService
from pixelcopy.ui.pages.extract import ExtractPage


class ImageImportController(QObject):
    """Coordinate file and clipboard imports without placing decoding in widgets."""

    document_imported = Signal(object)
    document_cleared = Signal()

    def __init__(
        self,
        application: QApplication,
        page: ExtractPage,
        service: ImageImportService,
    ) -> None:
        super().__init__(page)
        self._application = application
        self._page = page
        self._service = service
        page.file_selected.connect(self.import_file)
        page.paste_requested.connect(self.import_clipboard)
        page.source_cleared.connect(self.clear)

    def import_file(self, path: Path) -> None:
        """Validate and present a selected or dropped file."""
        try:
            document = self._service.load_file(path)
        except ImageImportError as error:
            self._page.display_error(str(error))
            return
        self._page.display_document(document)
        self.document_imported.emit(document)

    def import_clipboard(self) -> None:
        """Encode a clipboard image locally and pass it through the same validator."""
        image = self._application.clipboard().image()
        if image.isNull():
            self._page.display_error("The clipboard does not contain an image.")
            return
        self.import_qimage(image, "Clipboard image")

    def import_qimage(self, image: QImage, source_name: str) -> None:
        """Encode a Qt image locally and pass it through content validation."""
        buffer = QBuffer()
        qt_png_format = cast(bytes, "PNG")
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly) or not image.save(
            buffer, qt_png_format
        ):
            self._page.display_error("PixelCopy could not read the clipboard image.")
            return
        try:
            raw_content = buffer.data().data()
            content = raw_content if isinstance(raw_content, bytes) else bytes(raw_content)
            document = self._service.load_bytes(content, source_name)
        except ImageImportError as error:
            self._page.display_error(str(error))
            return
        finally:
            buffer.close()
        self._page.display_document(document)
        self.document_imported.emit(document)

    def clear(self) -> None:
        """Clear presentation state and notify dependent workflows."""
        self._page.clear_source()
        self.document_cleared.emit()
