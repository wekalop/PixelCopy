"""Export format selection."""

from __future__ import annotations

from pathlib import Path

from pixelcopy.domain.export import ExportFormat, ExportPayload
from pixelcopy.export.base import Exporter
from pixelcopy.export.searchable_pdf_exporter import SearchablePDFExporter
from pixelcopy.export.text_exporters import (
    CSVExporter,
    JSONExporter,
    MarkdownExporter,
    TextExporter,
)


class ExportService:
    def __init__(self) -> None:
        self._exporters: dict[ExportFormat, Exporter] = {
            ExportFormat.TEXT: TextExporter(),
            ExportFormat.MARKDOWN: MarkdownExporter(),
            ExportFormat.JSON: JSONExporter(),
            ExportFormat.CSV: CSVExporter(),
            ExportFormat.SEARCHABLE_PDF: SearchablePDFExporter(),
        }

    def export(
        self, payload: ExportPayload, destination: Path, export_format: ExportFormat
    ) -> None:
        self._exporters[export_format].export(payload, destination)
