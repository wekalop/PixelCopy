from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QKeySequence
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.app import ApplicationController
from pixelcopy.config.settings import SettingsStore
from pixelcopy.controllers.capture_controller import CaptureController
from pixelcopy.ui.main_window import MainWindow
from pixelcopy.ui.pages.settings import SettingsPage
from pixelcopy.ui.styles.theme import Theme, stylesheet


def test_capture_shortcut_recorder_accepts_two_key_combination(qtbot: QtBot) -> None:
    page = SettingsPage("light")
    qtbot.addWidget(page)
    captured: list[str] = []
    page.shortcut_changed.connect(captured.append)

    page.shortcut_editor.setKeySequence(QKeySequence("Ctrl+X"))
    page.shortcut_editor.editingFinished.emit()

    assert captured == ["Ctrl+X"]
    assert page.shortcut_editor.maximumSequenceLength() == 1


def test_registered_capture_shortcut_persists_and_updates_tooltip(
    qtbot: QtBot,
    qapp: QApplication,
    tmp_path: Path,
    monkeypatch,
) -> None:
    store = SettingsStore(tmp_path / "settings.json")
    controller = ApplicationController(qapp, store)
    qtbot.addWidget(controller.window)
    monkeypatch.setattr(controller.capture_controller, "register_shortcut", lambda value: True)

    controller.change_shortcut("Ctrl+X")

    assert store.load().global_shortcut == "Ctrl+X"
    assert "Ctrl+X" in controller.window.extract_page.capture_button.toolTip()


def test_extract_controls_keep_readable_widths_at_minimum_window_size(qtbot: QtBot) -> None:
    window = MainWindow()
    window.resize(window.minimumSize().expandedTo(QSize(1100, 720)))
    qtbot.addWidget(window)
    window.show()
    qtbot.wait(10)
    page = window.extract_page

    assert page.copy_button.text() == "Copy text"
    assert page.copy_button.width() >= page.copy_button.sizeHint().width()
    assert page.mode_selector.width() >= page.mode_selector.sizeHint().width()
    assert page.preprocessing_panel.profile.width() >= 80


def test_light_theme_styles_combo_popup_and_numeric_inputs() -> None:
    light = stylesheet(Theme.LIGHT)

    assert "QComboBox QAbstractItemView" in light
    assert "QDoubleSpinBox" in light
    assert "QKeySequenceEdit" in light


def test_capture_result_restores_a_minimized_window(qtbot: QtBot, qapp: QApplication) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    imported: list[tuple[QImage, str]] = []

    class ImageImportStub:
        def import_qimage(self, image: QImage, source: str) -> None:
            imported.append((image, source))

    controller = CaptureController(qapp, window.extract_page, ImageImportStub())  # type: ignore[arg-type]
    window.showMinimized()
    qtbot.waitUntil(window.isMinimized)

    controller._captured(QImage(10, 10, QImage.Format.Format_RGB32))
    qtbot.waitUntil(lambda: not window.isMinimized())

    assert imported[0][1] == "Screen capture"
    controller.close()
