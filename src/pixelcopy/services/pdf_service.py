"""Memory-conscious local PDF inspection and rendering."""

from __future__ import annotations

from pathlib import Path

import pymupdf as fitz

from pixelcopy.domain.exceptions import PixelCopyError
from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.pdf import PDFDocumentInfo


class PDFError(PixelCopyError):
    """A PDF is unreadable, invalid, encrypted, or has an invalid page selection."""


def parse_page_range(value: str, page_count: int) -> tuple[int, ...]:
    """Parse user-facing one-based pages into sorted unique zero-based indexes."""
    if page_count < 1:
        raise PDFError("This PDF has no pages.")
    text = value.strip()
    if not text or text.lower() == "all":
        return tuple(range(page_count))
    pages: set[int] = set()
    try:
        for part in text.split(","):
            bounds = [int(item.strip()) for item in part.split("-")]
            if len(bounds) == 1:
                start = end = bounds[0]
            elif len(bounds) == 2:
                start, end = bounds
            else:
                raise ValueError
            if start < 1 or end < start or end > page_count:
                raise ValueError
            pages.update(range(start - 1, end))
    except ValueError as error:
        raise PDFError(f"Enter pages from 1 to {page_count}, for example 1-3,5.") from error
    return tuple(sorted(pages))


class PDFService:
    """Open documents briefly and render only the requested page."""

    def inspect(self, path: Path) -> PDFDocumentInfo:
        try:
            with fitz.open(path) as document:  # type: ignore[no-untyped-call]
                if document.needs_pass:
                    raise PDFError("Password-protected PDFs are not supported yet.")
                if not document.is_pdf or document.page_count < 1:
                    raise PDFError("This file is not a valid PDF document.")
                metadata = document.metadata or {}
                title_value = metadata.get("title", "")
                title = title_value.strip() if isinstance(title_value, str) else ""
                return PDFDocumentInfo(path, document.page_count, title or path.stem)
        except PDFError:
            raise
        except (fitz.FileDataError, OSError, RuntimeError) as error:
            raise PDFError("PixelCopy could not open this PDF. It may be damaged.") from error

    def render_page(self, path: Path, page_index: int, dpi: int = 300) -> ImageDocument:
        """Render one page and close the document before returning its pixels."""
        if not 72 <= dpi <= 600:
            raise PDFError("PDF resolution must be between 72 and 600 DPI.")
        try:
            with fitz.open(path) as document:  # type: ignore[no-untyped-call]
                if not 0 <= page_index < document.page_count:
                    raise PDFError(f"Page {page_index + 1} is outside this document.")
                page = document.load_page(page_index)
                pixmap = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=True)
                return ImageDocument(
                    source_name=f"{path.name} · page {page_index + 1}",
                    image_format="PDF",
                    width=pixmap.width,
                    height=pixmap.height,
                    color_mode="RGBA",
                    rgba_pixels=pixmap.samples,
                    original_path=path,
                )
        except PDFError:
            raise
        except (fitz.FileDataError, OSError, RuntimeError) as error:
            raise PDFError(f"Could not render page {page_index + 1}: {error}") from error

    def render_thumbnail(self, path: Path, page_index: int, width: int = 160) -> ImageDocument:
        """Render a small page preview without retaining the PDF in memory."""
        full = self.render_page(path, page_index, dpi=96)
        if full.width <= width:
            return full
        from PIL import Image

        image = Image.frombytes("RGBA", (full.width, full.height), full.rgba_pixels)
        height = max(1, round(full.height * width / full.width))
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        return ImageDocument(
            source_name=full.source_name,
            image_format="PDF thumbnail",
            width=width,
            height=height,
            color_mode="RGBA",
            rgba_pixels=resized.tobytes(),
            original_path=path,
        )
