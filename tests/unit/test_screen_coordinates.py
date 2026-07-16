from __future__ import annotations

import pytest
from PySide6.QtCore import QRect

from pixelcopy.services.global_shortcut import ShortcutRegistrationError, parse_shortcut
from pixelcopy.services.screenshot_service import logical_to_physical_rect


def test_negative_monitor_coordinates_map_to_local_physical_pixels() -> None:
    screen = QRect(-1920, 0, 1920, 1080)
    selection = QRect(-1900, 10, 100, 50)

    assert logical_to_physical_rect(selection, screen, 1.5) == QRect(30, 15, 150, 75)


def test_global_shortcut_parser_supports_default_and_function_keys() -> None:
    assert parse_shortcut("Ctrl+Shift+X") == (0x0002 | 0x0004, ord("X"))
    assert parse_shortcut("Alt+F12") == (0x0001, 0x7B)


def test_global_shortcut_parser_rejects_unmodified_key() -> None:
    with pytest.raises(ShortcutRegistrationError, match="modifier"):
        parse_shortcut("X")
