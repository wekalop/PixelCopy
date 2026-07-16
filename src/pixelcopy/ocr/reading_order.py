"""Deterministic geometric reading-order reconstruction."""

from __future__ import annotations

from pixelcopy.domain.ocr import OCRBlock


def sort_reading_order(
    blocks: tuple[OCRBlock, ...], right_to_left: bool = False
) -> tuple[OCRBlock, ...]:
    """Group blocks into visual lines, then sort each line directionally."""
    if len(blocks) < 2:
        return blocks

    by_vertical_position = sorted(blocks, key=lambda block: block.bounds.center_y)
    lines: list[list[OCRBlock]] = []
    for block in by_vertical_position:
        if not lines:
            lines.append([block])
            continue
        current_line = lines[-1]
        average_center = sum(item.bounds.center_y for item in current_line) / len(current_line)
        tolerance = max(block.bounds.height, *(item.bounds.height for item in current_line)) * 0.6
        if abs(block.bounds.center_y - average_center) <= tolerance:
            current_line.append(block)
        else:
            lines.append([block])

    ordered: list[OCRBlock] = []
    for line in lines:
        line.sort(key=lambda block: block.bounds.left, reverse=right_to_left)
        ordered.extend(line)
    return tuple(ordered)


def text_from_blocks(blocks: tuple[OCRBlock, ...], right_to_left: bool = False) -> str:
    """Build plain text while retaining visual line boundaries."""
    ordered = sort_reading_order(blocks, right_to_left)
    if not ordered:
        return ""

    lines: list[list[OCRBlock]] = []
    for block in ordered:
        if not lines:
            lines.append([block])
            continue
        previous_line = lines[-1]
        center = sum(item.bounds.center_y for item in previous_line) / len(previous_line)
        tolerance = max(block.bounds.height, *(item.bounds.height for item in previous_line)) * 0.6
        if abs(block.bounds.center_y - center) <= tolerance:
            previous_line.append(block)
        else:
            lines.append([block])
    return "\n".join(" ".join(block.text for block in line) for line in lines)
