"""Virtual-desktop rectangular selection overlay."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget

from pixelcopy.services.screenshot_service import ScreenshotService, virtual_desktop_geometry


class ScreenCaptureOverlay(QWidget):
    """Dim all monitors and capture a user-selected physical-pixel region."""

    captured = Signal(object)
    cancelled = Signal()

    def __init__(self, service: ScreenshotService) -> None:
        super().__init__(None)
        self._service = service
        self._origin: QPoint | None = None
        self._cursor = QPoint()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setGeometry(virtual_desktop_geometry())

    def begin(self) -> None:
        self._origin = None
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(8, 15, 30, 145))
        selection = self._selection()
        if not selection.isEmpty():
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(selection, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.setPen(QPen(QColor("#60A5FA"), 2))
            painter.drawRect(selection)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin = event.position().toPoint()
            self._cursor = self._origin
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._cursor = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._origin is None:
            return
        self._cursor = event.position().toPoint()
        local_selection = self._selection()
        if local_selection.width() < 3 or local_selection.height() < 3:
            self._origin = None
            self.update()
            return
        global_selection = local_selection.translated(self.geometry().topLeft())
        self.hide()
        self.captured.emit(self._service.capture_region(global_selection))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.cancelled.emit()
            return
        super().keyPressEvent(event)

    def _selection(self) -> QRect:
        if self._origin is None:
            return QRect()
        return QRect(self._origin, self._cursor).normalized()
