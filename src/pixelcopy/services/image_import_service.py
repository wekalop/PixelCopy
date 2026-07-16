"""Content-validated local image loading."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from pixelcopy.domain.exceptions import CorruptImageError, UnsupportedImageError
from pixelcopy.domain.images import ImageDocument

SUPPORTED_IMAGE_FORMATS = frozenset({"PNG", "JPEG", "BMP", "TIFF", "WEBP"})
IMAGE_FILE_FILTER = "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp)"


class ImageImportService:
    """Validate and decode images without modifying their sources."""

    def load_file(self, path: Path) -> ImageDocument:
        """Load an image by content rather than trusting its extension."""
        try:
            content = path.read_bytes()
        except OSError as error:
            raise CorruptImageError(f"Could not read '{path.name}': {error}") from error
        return self.load_bytes(content, source_name=path.name, original_path=path)

    def load_bytes(
        self,
        content: bytes,
        source_name: str = "Clipboard image",
        original_path: Path | None = None,
    ) -> ImageDocument:
        """Validate encoded bytes and normalize decoded pixels to RGBA."""
        if not content:
            raise CorruptImageError("The image is empty.")

        try:
            with Image.open(io.BytesIO(content)) as candidate:
                detected_format = (candidate.format or "").upper()
                if detected_format not in SUPPORTED_IMAGE_FORMATS:
                    raise UnsupportedImageError(
                        "This image format is not supported. Use PNG, JPEG, BMP, TIFF, or WebP."
                    )
                candidate.verify()

            with Image.open(io.BytesIO(content)) as decoded:
                corrected = ImageOps.exif_transpose(decoded)
                corrected.load()
                rgba = corrected.convert("RGBA")
                width, height = rgba.size
                if width < 1 or height < 1:
                    raise CorruptImageError("The image has invalid dimensions.")
                return ImageDocument(
                    source_name=source_name,
                    image_format="JPEG" if detected_format == "JPG" else detected_format,
                    width=width,
                    height=height,
                    color_mode=decoded.mode,
                    rgba_pixels=rgba.tobytes(),
                    original_path=original_path,
                )
        except UnsupportedImageError:
            raise
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError) as error:
            raise CorruptImageError(
                "PixelCopy could not open this image. It may be damaged or unsafe."
            ) from error
