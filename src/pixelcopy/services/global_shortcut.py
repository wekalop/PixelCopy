"""Windows RegisterHotKey lifecycle integration."""

import ctypes
import ctypes.wintypes
import sys
import threading
from typing import Any, Protocol, cast

from PySide6.QtCore import QObject, Signal


class ShortcutRegistrationError(RuntimeError):
    """A global shortcut is invalid, unsupported, or already occupied."""


class _NativeFunction(Protocol):
    argtypes: list[object]
    restype: object

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


class WindowsGlobalShortcut(QObject):
    """Own a Windows hotkey on a dedicated native message-loop thread."""

    activated = Signal()
    HOTKEY_ID = 0x5043

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._registered = False
        self._modifiers = 0
        self._key_code = 0
        self._thread: threading.Thread | None = None
        self._thread_id = 0
        self._ready = threading.Event()
        self._registration_succeeded = False

    def register(self, shortcut: str) -> None:
        if sys.platform != "win32":
            raise ShortcutRegistrationError("Global capture shortcuts currently require Windows.")
        modifiers, key_code = parse_shortcut(shortcut)
        previous = (self._registered, self._modifiers, self._key_code)
        self.unregister()
        if not self._start_worker(modifiers, key_code):
            restored = False
            if previous[0]:
                restored = self._start_worker(previous[1], previous[2])
                if restored:
                    self._registered = True
                    self._modifiers = previous[1]
                    self._key_code = previous[2]
            raise ShortcutRegistrationError(
                f"Could not register {shortcut}. Another application may already use it."
                + (" The previous shortcut remains active." if restored else "")
            )
        self._registered = True
        self._modifiers = modifiers
        self._key_code = key_code

    def unregister(self) -> None:
        if self._thread is None:
            self._registered = False
            return
        if self._thread_id:
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            post_thread_message = cast(Any, user32.PostThreadMessageW)
            post_thread_message.argtypes = [
                ctypes.wintypes.DWORD,
                ctypes.wintypes.UINT,
                ctypes.wintypes.WPARAM,
                ctypes.wintypes.LPARAM,
            ]
            post_thread_message.restype = ctypes.wintypes.BOOL
            post_thread_message(self._thread_id, 0x0012, 0, 0)
        self._thread.join(timeout=2.0)
        self._thread = None
        self._thread_id = 0
        self._registered = False
        self._modifiers = 0
        self._key_code = 0

    def close(self) -> None:
        """Release the registered hotkey and stop its native message loop."""
        self.unregister()

    def _start_worker(self, modifiers: int, key_code: int) -> bool:
        self._ready.clear()
        self._registration_succeeded = False
        self._thread = threading.Thread(
            target=self._message_loop,
            args=(modifiers, key_code),
            name="PixelCopyGlobalShortcut",
            daemon=True,
        )
        self._thread.start()
        if not self._ready.wait(timeout=2.0):
            self.unregister()
            return False
        if not self._registration_succeeded:
            self._thread.join(timeout=2.0)
            self._thread = None
            self._thread_id = 0
            return False
        return True

    def _message_loop(self, modifiers: int, key_code: int) -> None:
        register_hot_key, unregister_hot_key = self._native_functions()
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        get_current_thread_id = cast(Any, kernel32.GetCurrentThreadId)
        get_current_thread_id.argtypes = []
        get_current_thread_id.restype = ctypes.wintypes.DWORD
        get_message = cast(Any, user32.GetMessageW)
        get_message.argtypes = [
            ctypes.POINTER(ctypes.wintypes.MSG),
            ctypes.wintypes.HWND,
            ctypes.wintypes.UINT,
            ctypes.wintypes.UINT,
        ]
        get_message.restype = ctypes.wintypes.BOOL
        peek_message = cast(Any, user32.PeekMessageW)
        peek_message.argtypes = [
            ctypes.POINTER(ctypes.wintypes.MSG),
            ctypes.wintypes.HWND,
            ctypes.wintypes.UINT,
            ctypes.wintypes.UINT,
            ctypes.wintypes.UINT,
        ]
        peek_message.restype = ctypes.wintypes.BOOL
        self._thread_id = int(get_current_thread_id())
        message = ctypes.wintypes.MSG()
        peek_message(ctypes.byref(message), None, 0, 0, 0)
        self._registration_succeeded = bool(
            register_hot_key(0, self.HOTKEY_ID, modifiers, key_code)
        )
        self._ready.set()
        if not self._registration_succeeded:
            return
        try:
            while get_message(ctypes.byref(message), None, 0, 0) > 0:
                if message.message == 0x0312 and int(message.wParam) == self.HOTKEY_ID:
                    self.activated.emit()
        finally:
            unregister_hot_key(0, self.HOTKEY_ID)

    @staticmethod
    def _native_functions() -> tuple[_NativeFunction, _NativeFunction]:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        register_hot_key = cast(_NativeFunction, user32.RegisterHotKey)
        register_hot_key.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.c_int,
            ctypes.wintypes.UINT,
            ctypes.wintypes.UINT,
        ]
        register_hot_key.restype = ctypes.wintypes.BOOL
        unregister_hot_key = cast(_NativeFunction, user32.UnregisterHotKey)
        unregister_hot_key.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
        unregister_hot_key.restype = ctypes.wintypes.BOOL
        return register_hot_key, unregister_hot_key

    @property
    def is_registered(self) -> bool:
        """Return whether Windows currently owns this application's hotkey."""
        return self._registered
