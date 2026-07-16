from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.app import ApplicationController
from pixelcopy.config.settings import SettingsStore
from pixelcopy.domain.preprocessing import PreprocessingOptions
from pixelcopy.ocr.fake_engine import FakeOCREngine


def test_processed_preview_is_created_and_reset(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 5), "white").save(buffer, "PNG")
    path = tmp_path / "source.png"
    path.write_bytes(buffer.getvalue())
    controller = ApplicationController(
        qapp, SettingsStore(tmp_path / "settings.json"), FakeOCREngine()
    )
    qtbot.addWidget(controller.window)
    controller.image_import_controller.import_file(path)

    controller.preprocessing_controller.process(
        PreprocessingOptions(rotation_degrees=90, upscale_factor=2.0)
    )
    page = controller.window.extract_page
    qtbot.waitUntil(lambda: page.preview_tabs.isTabEnabled(1))

    assert page.preview_tabs.currentIndex() == 1
    controller.preprocessing_controller.reset()
    assert page.preview_tabs.currentIndex() == 0
    assert not page.preview_tabs.isTabEnabled(1)
