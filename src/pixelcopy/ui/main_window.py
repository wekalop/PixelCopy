"""PixelCopy top-level desktop window."""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from pixelcopy.config.constants import APP_NAME
from pixelcopy.ui.navigation import NavigationSidebar
from pixelcopy.ui.pages.extract import ExtractPage
from pixelcopy.ui.pages.pdf import PDFPage
from pixelcopy.ui.pages.placeholder import AboutPage, PlaceholderPage
from pixelcopy.ui.pages.settings import SettingsPage


class MainWindow(QMainWindow):
    """Application shell coordinating navigation between top-level pages."""

    def __init__(
        self,
        theme: str = "light",
        shortcut: str = "Ctrl+Shift+X",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setWindowTitle(APP_NAME)
        self.resize(QSize(1180, 760))
        self.setMinimumSize(QSize(900, 620))

        root = QWidget()
        root.setObjectName("appRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        self.navigation = NavigationSidebar()
        self.pages = QStackedWidget()
        self._page_indexes: dict[str, int] = {}
        root_layout.addWidget(self.navigation)
        root_layout.addWidget(self.pages, 1)

        self.extract_page = ExtractPage()
        self._add_page("extract", self.extract_page)
        self.pdf_page = PDFPage()
        self._add_page("pdf", self.pdf_page)
        self._add_page(
            "history",
            PlaceholderPage(
                "History",
                "Optionally save, search, favorite, and manage local extractions.",
                "Milestone 8",
            ),
        )
        self.settings_page = SettingsPage(theme, shortcut)
        self._add_page("settings", self.settings_page)
        self._add_page("about", AboutPage())

        self.navigation.page_requested.connect(self.show_page)
        self.show_page("extract")
        self.statusBar().showMessage("Ready · local processing only")

    def _add_page(self, key: str, page: QWidget) -> None:
        self._page_indexes[key] = self.pages.addWidget(page)

    def show_page(self, key: str) -> None:
        """Display a registered page and synchronize navigation state."""
        index = self._page_indexes.get(key)
        if index is None:
            return
        self.pages.setCurrentIndex(index)
        self.navigation.select(key)

    @property
    def current_page_key(self) -> str:
        """Return the stable key for the visible page."""
        current_index = self.pages.currentIndex()
        return next(key for key, index in self._page_indexes.items() if index == current_index)
