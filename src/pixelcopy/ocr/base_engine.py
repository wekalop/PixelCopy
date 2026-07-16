"""Shared OCR engine contract."""

from __future__ import annotations

from typing import Protocol

from pixelcopy.domain.ocr import OCRRequest, OCRResult


class OCREngine(Protocol):
    """A local text-recognition engine."""

    @property
    def name(self) -> str:
        """Return the stable engine name shown in results."""
        ...

    def recognize(self, request: OCRRequest) -> OCRResult:
        """Recognize text from a validated request."""
        ...
