"""Preload official local PaddleOCR models before packaging or first use."""

from __future__ import annotations

import argparse
import importlib
from collections.abc import Callable
from typing import cast


def preload_languages(languages: tuple[str, ...]) -> None:
    """Initialize each requested model without processing user content."""
    try:
        module = importlib.import_module("paddleocr")
    except ImportError as error:
        raise RuntimeError(
            'PaddleOCR is not installed. Run: python -m pip install -e ".[ocr]"'
        ) from error
    factory = cast(Callable[..., object], module.PaddleOCR)
    for language in languages:
        print(f"Preparing the official local PaddleOCR '{language}' model...")
        factory(
            lang=language,
            use_doc_orientation_classify=True,
            use_doc_unwarping=False,
            use_textline_orientation=True,
            device="cpu",
            enable_mkldnn=False,
        )
    print("Local OCR model setup completed. No document content was processed.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--languages",
        nargs="+",
        choices=("en", "ar"),
        default=("en", "ar"),
        help="Official PaddleOCR language models to preload",
    )
    options = parser.parse_args()
    preload_languages(tuple(options.languages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
