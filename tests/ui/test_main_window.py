from __future__ import annotations

from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from pixelcopy.ui.main_window import MainWindow


def test_sidebar_navigation_changes_visible_page(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    assert window.current_page_key == "extract"

    qtbot.mouseClick(window.navigation.button_for("pdf"), Qt.MouseButton.LeftButton)

    assert window.current_page_key == "pdf"
    assert window.navigation.button_for("pdf").isChecked()


def test_every_required_page_is_registered(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    for key in ("extract", "pdf", "history", "settings", "about"):
        window.show_page(key)
        assert window.current_page_key == key
