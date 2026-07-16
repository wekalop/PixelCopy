from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.app import ApplicationController
from pixelcopy.config.settings import SettingsStore
from pixelcopy.ocr.fake_engine import FakeOCREngine


def test_result_edit_actions_and_cleanup_are_keyboard_accessible(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    controller = ApplicationController(
        qapp,
        SettingsStore(tmp_path / "settings.json"),
        FakeOCREngine(),
    )
    page = controller.window.extract_page
    qtbot.addWidget(controller.window)
    page.result_editor.setPlainText("  docu-\nment   text  \n\n\nnext")

    controller.ocr_controller.cleanup_result("normalize_whitespace")
    controller.ocr_controller.cleanup_result("join_hyphenated_linebreaks")
    controller.ocr_controller.cleanup_result("remove_duplicate_blank_lines")

    assert page.result_editor.toPlainText() == "document text\n\nnext"
    assert page.copy_button.isEnabled()
    page.wrap_button.click()
    assert page.result_editor.wordWrapMode() is QTextOption.WrapMode.NoWrap
    page.clear_result_button.click()
    assert page.result_editor.toPlainText() == ""
    assert not page.copy_button.isEnabled()


def test_find_replace_reports_matches(qtbot: QtBot) -> None:
    from PySide6.QtWidgets import QPlainTextEdit

    from pixelcopy.ui.dialogs.find_replace import FindReplaceDialog

    editor = QPlainTextEdit()
    editor.setPlainText("one two one")
    dialog = FindReplaceDialog(editor)
    qtbot.addWidget(editor)
    qtbot.addWidget(dialog)
    dialog.find_editor.setText("one")
    dialog.replace_editor.setText("three")

    assert dialog.replace_all() == 2
    assert editor.toPlainText() == "three two three"
    assert dialog.status.text() == "Replaced 2 match(es)."
