"""Text, Markdown, JSON, and block CSV exporters."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from pixelcopy.domain.export import ExportPayload
from pixelcopy.export.base import validate_destination


class TextExporter:
    def export(self, payload: ExportPayload, destination: Path) -> None:
        validate_destination(destination)
        destination.write_text(payload.edited_text, encoding="utf-8")


class MarkdownExporter(TextExporter):
    pass


class JSONExporter:
    def export(self, payload: ExportPayload, destination: Path) -> None:
        validate_destination(destination)
        data = {
            "text": payload.edited_text,
            "ocr": asdict(payload.result),
        }
        destination.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


class CSVExporter:
    def export(self, payload: ExportPayload, destination: Path) -> None:
        validate_destination(destination)
        with destination.open("x", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["page", "text", "confidence", "left", "top", "right", "bottom"])
            for block in payload.result.blocks:
                writer.writerow(
                    [
                        block.page_number or payload.result.page_number or 1,
                        block.text,
                        block.confidence,
                        block.bounds.left,
                        block.bounds.top,
                        block.bounds.right,
                        block.bounds.bottom,
                    ]
                )
