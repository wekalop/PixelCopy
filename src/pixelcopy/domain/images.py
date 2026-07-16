"""Image source models shared across services and presentation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ImageDocument:
    """A validated, decoded image represented as immutable RGBA pixels."""

    source_name: str
    image_format: str
    width: int
    height: int
    color_mode: str
    rgba_pixels: bytes
    original_path: Path | None = None

    @property
    def pixel_count(self) -> int:
        """Return the decoded image area."""
        return self.width * self.height

    @property
    def dimensions_label(self) -> str:
        """Return compact user-facing dimensions."""
        return f"{self.width} x {self.height} px"
