from __future__ import annotations

import ctypes
import ctypes.wintypes
import sys

import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.services.global_shortcut import (
    ShortcutRegistrationError,
    WindowsGlobalShortcut,
    parse_shortcut,
)
from pixelcopy.services.screenshot_service import logical_to_physical_rect


def test_negative_monitor_coordinates_map_to_local_physical_pixels() -> None:
    screen = QRect(-1920, 0, 1920, 1080)
    selection = QRect(-1900, 10, 100, 50)

    assert logical_to_physical_rect(selection, screen, 1.5) == QRect(30, 15, 150, 75)


def test_global_shortcut_parser_supports_default_and_function_keys() -> None:
    assert parse_shortcut("Ctrl+Shift+X") == (0x0002 | 0x0004, ord("X"))
    assert parse_shortcut("Ctrl+X") == (0x0002, ord("X"))
    assert parse_shortcut("Alt+F12") == (0x0001, 0x7B)


def test_global_shortcut_parser_rejects_unmodified_key() -> None:
    with pytest.raises(ShortcutRegistrationError, match="modifier"):
        parse_shortcut("X")


@pytest.mark.skipif(sys.platform != "win32", reason="Windows RegisterHotKey integration")
def test_global_shortcut_worker_delivers_hotkey_while_qt_is_running(
    qtbot: QtBot,
    qapp: QApplication,
) -> None:
    shortcut = WindowsGlobalShortcut()
    activated: list[bool] = []
    shortcut.activated.connect(lambda: activated.append(True))
    shortcut.register("Ctrl+Shift+F24")
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    post_thread_message = user32.PostThreadMessageW
    post_thread_message.argtypes = [
        ctypes.wintypes.DWORD,
        ctypes.wintypes.UINT,
        ctypes.wintypes.WPARAM,
        ctypes.wintypes.LPARAM,
    ]
    post_thread_message.restype = ctypes.wintypes.BOOL

    try:
        assert post_thread_message(shortcut._thread_id, 0x0312, shortcut.HOTKEY_ID, 0)
        qtbot.waitUntil(lambda: activated == [True], timeout=1_000)
        assert shortcut.is_registered
    finally:
        shortcut.close()

    assert not shortcut.is_registered
