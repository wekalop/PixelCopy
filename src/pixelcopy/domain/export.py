"""Export payload and format models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import OCRResult


class ExportFormat(StrEnum):
    TEXT = "txt"
    MARKDOWN = "md"
    JSON = "json"
    CSV = "csv"
    SEARCHABLE_PDF = "pdf"


@dataclass(frozen=True, slots=True)
class ExportPayload:
    edited_text: str
    result: OCRResult
    source_images: tuple[ImageDocument, ...] = ()
