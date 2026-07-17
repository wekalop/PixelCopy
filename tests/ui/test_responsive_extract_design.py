from __future__ import annotations

import pytest
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QAbstractButton, QCheckBox, QComboBox, QSpinBox
from pytestqt.qtbot import QtBot

from pixelcopy.ui.main_window import MainWindow
from pixelcopy.ui.styles.theme import Theme, stylesheet, tokens


@pytest.mark.parametrize(
    "size",
    (QSize(1024, 720), QSize(1280, 800), QSize(1440, 900), QSize(1920, 1080)),
)
def test_extract_workspace_preserves_usable_geometry(qtbot: QtBot, size: QSize) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(size)
    window.show()
    qtbot.wait(10)
    page = window.extract_page

    assert page.preview_tabs.height() >= 170
    assert page.result_editor.height() >= 190
    assert page.mode_selector.height() >= page.mode_selector.sizeHint().height()
    assert page.confidence_selector.height() >= page.confidence_selector.sizeHint().height()
    assert page.extract_button.isVisibleTo(page)


def test_processing_controls_are_labeled_and_scrollable(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(1024, 720)
    window.show()
    panel = window.extract_page.preprocessing_panel
    panel.advanced_toggle.setChecked(True)
    qtbot.wait(10)

    checkboxes = panel.findChildren(QCheckBox)
    assert checkboxes
    assert all(checkbox.text().strip() for checkbox in checkboxes)
    assert panel.advanced_scroll.isVisibleTo(window.extract_page)
    assert panel.advanced_scroll.verticalScrollBar().maximum() > 0
    assert panel.cancel_button.isHidden()


def test_buttons_and_compound_controls_expose_readable_semantics(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(1024, 720)
    window.show()
    page = window.extract_page

    for button in page.findChildren(QAbstractButton):
        if button.isVisibleTo(page):
            assert button.text().strip() or button.accessibleName().strip()
            assert button.height() >= button.minimumSizeHint().height()
    for control_type in (QComboBox, QSpinBox):
        for control in page.findChildren(control_type):
            if control.isVisibleTo(page):
                assert control.height() >= control.sizeHint().height()


def test_confidence_is_a_visible_bounded_percentage(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    confidence = window.extract_page.confidence_selector

    assert confidence.minimum() == 0
    assert confidence.maximum() == 100
    assert confidence.suffix() == "%"
    assert confidence.text() == "50%"


def test_tab_chain_reaches_source_editor_and_primary_action(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    page = window.extract_page
    visited = set()
    current = page.open_button
    for _ in range(60):
        visited.add(current)
        current = current.nextInFocusChain()

    assert page.result_editor in visited
    assert page.extract_button in visited


def test_themes_share_semantic_tokens_and_complete_control_states() -> None:
    for theme in Theme:
        palette = tokens(theme)
        qss = stylesheet(theme)
        assert palette.text_primary != palette.background
        assert palette.disabled_foreground != palette.disabled_background
        assert "QCheckBox" in qss
        assert "QProgressBar" in qss
        assert "QScrollBar" in qss
        assert ":focus" in qss
        assert ":disabled" in qss
        assert "url(" not in qss
