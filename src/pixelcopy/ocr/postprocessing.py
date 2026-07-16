"""Deterministic OCR text cleanup utilities.

These helpers never infer, rewrite, or correct recognized content. They only
apply transformations explicitly selected by the user.
"""

from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    """Normalize horizontal whitespace while preserving paragraph boundaries."""
    lines = [re.sub(r"[\t\f\v ]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(lines)


def remove_duplicate_blank_lines(text: str) -> str:
    """Collapse runs of empty lines to one empty line."""
    return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", text)


def join_hyphenated_linebreaks(text: str) -> str:
    """Join words explicitly split by a hyphen followed by a line ending."""
    return re.sub(r"(?<=\w)-[ \t]*\r?\n[ \t]*(?=\w)", "", text)


CLEANUP_ACTIONS = {
    "normalize_whitespace": normalize_whitespace,
    "remove_duplicate_blank_lines": remove_duplicate_blank_lines,
    "join_hyphenated_linebreaks": join_hyphenated_linebreaks,
}


def apply_cleanup(text: str, action: str) -> str:
    """Apply a named cleanup action, rejecting unknown transformations."""
    try:
        cleanup = CLEANUP_ACTIONS[action]
    except KeyError as error:
        raise ValueError(f"Unknown cleanup action: {action}") from error
    return cleanup(text)
