from __future__ import annotations

from pixelcopy.domain.ocr import BoundingBox, OCRBlock
from pixelcopy.ocr.reading_order import sort_reading_order, text_from_blocks


def block(text: str, left: float, top: float) -> OCRBlock:
    return OCRBlock(text, BoundingBox(left, top, left + 20, top + 10), 0.9)


def test_reconstructs_lines_then_left_to_right_order() -> None:
    blocks = (block("bottom", 0, 30), block("world", 30, 0), block("hello", 0, 1))

    assert text_from_blocks(blocks) == "hello world\nbottom"


def test_right_to_left_reverses_horizontal_order_only() -> None:
    blocks = (block("right", 30, 0), block("left", 0, 0), block("next", 30, 30))

    assert [item.text for item in sort_reading_order(blocks, right_to_left=True)] == [
        "right",
        "left",
        "next",
    ]
