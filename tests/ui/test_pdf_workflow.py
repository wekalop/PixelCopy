from __future__ import annotations

from pathlib import Path

import fitz
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.app import ApplicationController
from pixelcopy.config.settings import SettingsStore
from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCRResult
from pixelcopy.ocr.fake_engine import FakeOCREngine


def test_pdf_thumbnails_and_background_extraction(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    path = tmp_path / "scan.pdf"
    document = fitz.open()
    document.new_page(width=80, height=60)
    document.new_page(width=80, height=60)
    document.save(path)
    document.close()
    raw = OCRResult(
        "page text",
        (OCRBlock("page text", BoundingBox(0, 0, 20, 10), 0.9),),
        "en",
        0.1,
        "Fake OCR",
        80,
        60,
    )
    controller = ApplicationController(
        qapp, SettingsStore(tmp_path / "settings.json"), FakeOCREngine(raw)
    )
    qtbot.addWidget(controller.window)

    controller.pdf_controller.open_pdf(path)
    page = controller.window.pdf_page
    qtbot.waitUntil(
        lambda: page.thumbnails.item(0) is not None and not page.thumbnails.item(0).icon().isNull()
    )
    controller.pdf_controller.extract("all", 72, "en")
    qtbot.waitUntil(lambda: "--- Page 2 ---" in page.result_editor.toPlainText())

    assert page.thumbnails.count() == 2
    assert page.result_editor.toPlainText().count("page text") == 2
