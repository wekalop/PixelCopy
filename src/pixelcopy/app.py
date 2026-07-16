"""Qt application construction."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from pixelcopy.config.constants import APP_NAME, APP_ORGANIZATION, APP_VERSION


def create_application(arguments: Sequence[str] | None = None) -> QApplication:
    """Create or return the process-wide Qt application."""
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing

    app = QApplication(list(arguments) if arguments is not None else sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORGANIZATION)
    app.setApplicationVersion(APP_VERSION)
    app.setStyle("Fusion")
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
    return app
