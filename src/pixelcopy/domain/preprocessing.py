"""Typed image preprocessing configuration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ThresholdMode(StrEnum):
    NONE = "none"
    BINARY = "binary"
    ADAPTIVE = "adaptive"


class PreprocessingProfile(StrEnum):
    ORIGINAL = "original"
    AUTOMATIC = "automatic"
    SCANNED_DOCUMENT = "scanned_document"
    LOW_CONTRAST = "low_contrast"
    SMALL_TEXT = "small_text"
    DARK_BACKGROUND = "dark_background"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class PreprocessingOptions:
    """Explicit deterministic pipeline controls in execution order."""

    rotation_degrees: int = 0
    grayscale: bool = False
    contrast: float = 1.0
    brightness: int = 0
    denoise: bool = False
    sharpen: bool = False
    threshold: ThresholdMode = ThresholdMode.NONE
    invert: bool = False
    deskew: bool = False
    upscale_factor: float = 1.0

    def __post_init__(self) -> None:
        if self.rotation_degrees not in {0, 90, 180, 270}:
            raise ValueError("Rotation must be 0, 90, 180, or 270 degrees")
        if not 0.25 <= self.contrast <= 3.0:
            raise ValueError("Contrast must be between 0.25 and 3.0")
        if not -100 <= self.brightness <= 100:
            raise ValueError("Brightness must be between -100 and 100")
        if self.upscale_factor not in {1.0, 1.5, 2.0, 3.0, 4.0}:
            raise ValueError("Upscale factor is not supported")
