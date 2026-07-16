"""Result export UI coordination."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QFileDialog

from pixelcopy.domain.export import ExportFormat, ExportPayload
from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import OCRResult
from pixelcopy.export.base import ExportError
from pixelcopy.services.export_service import ExportService
from pixelcopy.ui.pages.extract import ExtractPage


class ExportController(QObject):
    def __init__(self, page: ExtractPage, service: ExportService) -> None:
        super().__init__(page)
        self._page = page
        self._service = service
        self._latest: tuple[OCRResult, ImageDocument] | None = None
        page.export_requested.connect(self.choose_destination)

    @Slot(object)
    def set_latest(self, value: object) -> None:
        if (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], OCRResult)
            and isinstance(value[1], ImageDocument)
        ):
            self._latest = (value[0], value[1])

    @Slot()
    def choose_destination(self) -> None:
        destination, selected_filter = QFileDialog.getSaveFileName(
            self._page,
            "Export recognized text",
            "",
            "Text (*.txt);;Markdown (*.md);;JSON (*.json);;CSV (*.csv);;Searchable PDF (*.pdf)",
        )
        if not destination:
            return
        suffixes = {
            "Text": ExportFormat.TEXT,
            "Markdown": ExportFormat.MARKDOWN,
            "JSON": ExportFormat.JSON,
            "CSV": ExportFormat.CSV,
            "Searchable PDF": ExportFormat.SEARCHABLE_PDF,
        }
        export_format = next(
            (value for label, value in suffixes.items() if selected_filter.startswith(label)),
            ExportFormat.TEXT,
        )
        self.export_to(Path(destination), export_format)

    def export_to(self, destination: Path, export_format: ExportFormat) -> None:
        """Export to a supplied path without opening a native dialog."""
        if self._latest is None:
            self._page.display_ocr_error("There is no OCR result to export.")
            return
        result, image = self._latest
        payload = ExportPayload(self._page.result_editor.toPlainText(), result, (image,))
        try:
            self._service.export(payload, destination, export_format)
        except (ExportError, OSError) as error:
            self._page.display_ocr_error(str(error))
            return
        self._page.result_status.setText(f"Exported to {destination.name}")
