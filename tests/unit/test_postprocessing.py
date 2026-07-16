from __future__ import annotations

import pytest

from pixelcopy.ocr.postprocessing import (
    apply_cleanup,
    join_hyphenated_linebreaks,
    normalize_whitespace,
    remove_duplicate_blank_lines,
)


def test_normalize_whitespace_preserves_paragraph_boundaries() -> None:
    assert normalize_whitespace("  first\t line  \n\n second   line ") == (
        "first line\n\nsecond line"
    )


def test_remove_duplicate_blank_lines_keeps_single_separator() -> None:
    assert remove_duplicate_blank_lines("one\n\n \n\n two") == "one\n\n two"


def test_join_hyphenated_linebreaks_only_joins_explicit_splits() -> None:
    assert join_hyphenated_linebreaks("docu-\nment\nwell-known") == "document\nwell-known"


def test_unknown_cleanup_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown cleanup action"):
        apply_cleanup("text", "rewrite")
