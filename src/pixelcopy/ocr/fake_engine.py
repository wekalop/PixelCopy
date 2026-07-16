"""Deterministic OCR engine for tests and development."""

from __future__ import annotations

from dataclasses import replace

from pixelcopy.domain.ocr import OCRRequest, OCRResult


class FakeOCREngine:
    """Return configured evidence without network access or model files."""

    def __init__(self, result: OCRResult | None = None, error: Exception | None = None) -> None:
        self._result = result
        self._error = error
        self.requests: list[OCRRequest] = []

    @property
    def name(self) -> str:
        return "Fake OCR"

    def recognize(self, request: OCRRequest) -> OCRResult:
        self.requests.append(request)
        if self._error is not None:
            raise self._error
        if self._result is not None:
            return replace(
                self._result,
                image_width=request.image.width,
                image_height=request.image.height,
            )
        return OCRResult(
            full_text="",
            blocks=(),
            recognition_language=request.options.language,
            duration_seconds=0.0,
            engine_name=self.name,
            image_width=request.image.width,
            image_height=request.image.height,
            warnings=("Fake engine returned no configured text.",),
        )
