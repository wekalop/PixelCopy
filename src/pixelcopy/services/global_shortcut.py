"""Windows RegisterHotKey lifecycle integration."""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import sys
from typing import Protocol, cast

from PySide6.QtCore import QAbstractNativeEventFilter, QByteArray, QObject, Signal
from PySide6.QtWidgets import QApplication


class ShortcutRegistrationError(RuntimeError):
    """A global shortcut is invalid, unsupported, or already occupied."""


class _NativeFunction(Protocol):
    def __call__(self, *arguments: int) -> int: ...


MODIFIERS = {"alt": 0x0001, "ctrl": 0x0002, "shift": 0x0004, "win": 0x0008}


def parse_shortcut(shortcut: str) -> tuple[int, int]:
    """Parse a conservative Windows global shortcut into native flags and key code."""
    parts = [part.strip().lower() for part in shortcut.split("+") if part.strip()]
    if len(parts) < 2:
        raise ShortcutRegistrationError("Use at least one modifier and one key.")
    key_name = parts[-1]
    modifiers = 0
    for part in parts[:-1]:
        if part not in MODIFIERS:
            raise ShortcutRegistrationError(f"Unsupported shortcut modifier: {part}")
        modifiers |= MODIFIERS[part]
    if len(key_name) == 1 and key_name.isalnum():
        key_code = ord(key_name.upper())
    elif key_name.startswith("f") and key_name[1:].isdigit() and 1 <= int(key_name[1:]) <= 24:
        key_code = 0x70 + int(key_name[1:]) - 1
    else:
        raise ShortcutRegistrationError(f"Unsupported shortcut key: {key_name}")
    return modifiers, key_code


class WindowsGlobalShortcut(QObject, QAbstractNativeEventFilter):
    """Register one application-wide shortcut and unregister it cleanly."""

    activated = Signal()
    HOTKEY_ID = 0x5043

    def __init__(self, application: QApplication) -> None:
        QObject.__init__(self)
        QAbstractNativeEventFilter.__init__(self)
        self._application = application
        self._registered = False

    def register(self, shortcut: str) -> None:
        if sys.platform != "win32":
            raise ShortcutRegistrationError("Global capture shortcuts currently require Windows.")
        self.unregister()
        modifiers, key_code = parse_shortcut(shortcut)
        register_hot_key, _ = self._native_functions()
        if not register_hot_key(0, self.HOTKEY_ID, modifiers, key_code):
            raise ShortcutRegistrationError(
                f"Could not register {shortcut}. Another application may already use it."
            )
        self._application.installNativeEventFilter(self)
        self._registered = True

    def unregister(self) -> None:
        if not self._registered:
            return
        _, unregister_hot_key = self._native_functions()
        unregister_hot_key(0, self.HOTKEY_ID)
        self._application.removeNativeEventFilter(self)
        self._registered = False

    def nativeEventFilter(
        self,
        event_type: QByteArray | bytes | bytearray | memoryview[int],
        message: int,
    ) -> tuple[bool, int]:
        del event_type
        if sys.platform == "win32" and message:
            msg = ctypes.wintypes.MSG.from_address(message)
            if msg.message == 0x0312 and int(msg.wParam) == self.HOTKEY_ID:
                self.activated.emit()
                return True, 0
        return False, 0

    @staticmethod
    def _native_functions() -> tuple[_NativeFunction, _NativeFunction]:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        return (
            cast(_NativeFunction, user32.RegisterHotKey),
            cast(_NativeFunction, user32.UnregisterHotKey),
        )

    def __del__(self) -> None:
        self.unregister()
