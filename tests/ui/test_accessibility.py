from __future__ import annotations

from pytestqt.qtbot import QtBot

from pixelcopy.ui.main_window import MainWindow


def test_extract_empty_and_loading_states_are_textual_and_accessible(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    page = window.extract_page

    assert page.source_status.text().startswith("Drop an image")
    assert page.result_status.text() == "Ready for a source image"
    assert page.result_status.accessibleName() == "Recognition status"
    assert page.progress.accessibleName() == "Recognition progress"
    assert not page.extract_button.isEnabled()
    assert not page.cancel_button.isEnabled()

    page.set_source_available(True)
    page.set_ocr_busy(True)
    assert page.progress.isVisibleTo(page)
    assert page.result_status.text() == "Recognizing text locally..."
    assert page.cancel_button.isEnabled()
    assert not page.extract_button.isEnabled()


def test_navigation_shortcuts_and_focus_names_are_exposed(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    for number, key in enumerate(("extract", "pdf", "history", "settings", "about"), 1):
        button = window.navigation.button_for(key)
        assert button.accessibleName().startswith("Open ")
        assert button.shortcut().toString() == f"Alt+{number}"
