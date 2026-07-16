from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.app import ApplicationController
from pixelcopy.config.settings import SettingsStore


def test_theme_selection_is_applied_and_persisted(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    store = SettingsStore(tmp_path / "settings.json")
    controller = ApplicationController(qapp, store)
    qtbot.addWidget(controller.window)

    selector = controller.window.settings_page.theme_selector
    selector.setCurrentIndex(selector.findData("dark"))

    assert qapp.property("pixelcopyTheme") == "dark"
    assert store.load().theme == "dark"
