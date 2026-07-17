from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_production_spec_preserves_paddlex_ocr_core_metadata() -> None:
    specification = (ROOT / "PixelCopy.spec").read_text(encoding="utf-8")

    for distribution in (
        "imagesize",
        "opencv-contrib-python",
        "pyclipper",
        "pypdfium2",
        "python-bidi",
        "shapely",
    ):
        assert f'"{distribution}"' in specification
    assert "copy_metadata(distribution)" in specification
