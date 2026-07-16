"""Image-backed PDF with invisible positional text."""

from __future__ import annotations

import io
from pathlib import Path

import pymupdf as fitz
from PIL import Image

from pixelcopy.domain.export import ExportPayload
from pixelcopy.export.base import ExportError, validate_destination


class SearchablePDFExporter:
    def export(self, payload: ExportPayload, destination: Path) -> None:
        validate_destination(destination)
        if not payload.source_images:
            raise ExportError("Searchable PDF export requires the source image or pages.")
        document = fitz.open()  # type: ignore[no-untyped-call]
        try:
            for page_number, image in enumerate(payload.source_images, start=1):
                page = document.new_page(width=image.width, height=image.height)
                encoded = io.BytesIO()
                Image.frombytes("RGBA", (image.width, image.height), image.rgba_pixels).save(
                    encoded, "PNG"
                )
                page.insert_image(  # type: ignore[no-untyped-call]
                    page.rect, stream=encoded.getvalue()
                )
                blocks = [
                    block
                    for block in payload.result.blocks
                    if (block.page_number or 1) == page_number
                ]
                for block in blocks:
                    bounds = fitz.Rect(  # type: ignore[no-untyped-call]
                        block.bounds.left,
                        block.bounds.top,
                        block.bounds.right,
                        block.bounds.bottom,
                    )
                    font_size = max(4.0, min(72.0, bounds.height * 0.7))
                    page.insert_text(
                        (bounds.x0, min(bounds.y1, bounds.y0 + font_size)),
                        block.text,
                        fontsize=font_size,
                        render_mode=3,
                    )
            document.save(destination)  # type: ignore[no-untyped-call]
        except Exception as error:
            raise ExportError(f"Could not create searchable PDF: {error}") from error
        finally:
            document.close()  # type: ignore[no-untyped-call]
