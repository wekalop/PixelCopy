"""OCR use-case orchestration."""

from __future__ import annotations

from dataclasses import replace

from pixelcopy.domain.ocr import OCRRequest, OCRResult
from pixelcopy.ocr.base_engine import OCREngine
from pixelcopy.ocr.reading_order import sort_reading_order, text_from_blocks


class OCRService:
    """Apply shared filtering and reading order around an engine adapter."""

    def __init__(self, engine: OCREngine) -> None:
        self._engine = engine

    @property
    def engine_name(self) -> str:
        return self._engine.name

    def recognize(self, request: OCRRequest) -> OCRResult:
        result = self._engine.recognize(request)
        retained = tuple(
            block
            for block in result.blocks
            if block.confidence >= request.options.confidence_threshold
        )
        rtl = request.options.language in {"ar", "en_ar"}
        ordered = sort_reading_order(retained, right_to_left=rtl)
        warnings = result.warnings
        removed_count = len(result.blocks) - len(retained)
        if removed_count:
            warnings += (f"{removed_count} low-confidence region(s) were excluded.",)
        return replace(
            result,
            full_text=text_from_blocks(ordered, right_to_left=rtl),
            blocks=ordered,
            warnings=warnings,
        )
