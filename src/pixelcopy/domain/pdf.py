"""Scanned PDF processing models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pixelcopy.domain.ocr import OCRResult


@dataclass(frozen=True, slots=True)
class PDFDocumentInfo:
    path: Path
    page_count: int
    title: str


@dataclass(frozen=True, slots=True)
class PDFPageFailure:
    page_number: int
    message: str


@dataclass(frozen=True, slots=True)
class PDFBatchResult:
    page_results: tuple[OCRResult, ...]
    failures: tuple[PDFPageFailure, ...]
    combined_text: str

    @property
    def page_count(self) -> int:
        return len(self.page_results) + len(self.failures)
