from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from pixelcopy.domain.exceptions import CorruptImageError, UnsupportedImageError
from pixelcopy.services.image_import_service import ImageImportService


def encoded_image(image_format: str, size: tuple[int, int] = (8, 5)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, "#2563EB").save(buffer, format=image_format)
    return buffer.getvalue()


@pytest.mark.parametrize("image_format", ["PNG", "JPEG", "BMP", "TIFF", "WEBP"])
def test_loads_every_supported_format_by_content(image_format: str) -> None:
    document = ImageImportService().load_bytes(encoded_image(image_format), "sample.bin")

    assert document.image_format == image_format
    assert (document.width, document.height) == (8, 5)
    assert len(document.rgba_pixels) == 8 * 5 * 4


def test_extension_does_not_override_detected_content(tmp_path: Path) -> None:
    path = tmp_path / "misleading.jpg"
    path.write_bytes(encoded_image("PNG"))

    document = ImageImportService().load_file(path)

    assert document.image_format == "PNG"
    assert document.original_path == path


def test_rejects_corrupt_image_content() -> None:
    with pytest.raises(CorruptImageError, match="could not open"):
        ImageImportService().load_bytes(b"not an image")


def test_rejects_decodable_but_unsupported_format() -> None:
    with pytest.raises(UnsupportedImageError, match="not supported"):
        ImageImportService().load_bytes(encoded_image("GIF"))
