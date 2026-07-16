"""Typed OCR inputs and results independent of recognition engines."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from pixelcopy.domain.images import ImageDocument


class OCRMode(StrEnum):
    """Recognition layout strategies supported by engine adapters."""

    PARAGRAPH = "paragraph"
    SINGLE_LINE = "single_line"
    SPARSE_TEXT = "sparse_text"
    TABLE = "table"


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-aligned text bounds in source-image pixels."""

    left: float
    top: float
    right: float
    bottom: float

    def __post_init__(self) -> None:
        if self.right < self.left or self.bottom < self.top:
            raise ValueError("Bounding box coordinates are inverted")

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    @property
    def center_y(self) -> float:
        return (self.top + self.bottom) / 2


@dataclass(frozen=True, slots=True)
class OCRBlock:
    """Recognized text and the evidence retained for its source region."""

    text: str
    bounds: BoundingBox
    confidence: float
    page_number: int | None = None
    region_metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("OCR confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class OCROptions:
    """Deterministic recognition options passed to an engine."""

    language: str = "en"
    mode: OCRMode = OCRMode.PARAGRAPH
    confidence_threshold: float = 0.5
    correct_orientation: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class OCRResult:
    """Complete OCR output without guessed or silently corrected content."""

    full_text: str
    blocks: tuple[OCRBlock, ...]
    recognition_language: str
    duration_seconds: float
    engine_name: str
    image_width: int
    image_height: int
    warnings: tuple[str, ...] = ()
    page_number: int | None = None

    @property
    def average_confidence(self) -> float:
        """Calculate the arithmetic mean confidence, or zero for no blocks."""
        if not self.blocks:
            return 0.0
        return sum(block.confidence for block in self.blocks) / len(self.blocks)


@dataclass(frozen=True, slots=True)
class OCRRequest:
    """Image and options forming one recognition job."""

    image: ImageDocument
    options: OCROptions
