"""Zoomable and pannable source image preview."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap, QWheelEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QWidget

from pixelcopy.domain.images import ImageDocument


class ImagePreview(QGraphicsView):
    """Display immutable image pixels with bounded zoom and hand panning."""

    MIN_SCALE = 0.1
    MAX_SCALE = 8.0

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("imagePreview")
        self.setAccessibleName("Source image preview")
        self.setScene(QGraphicsScene(self))
        self._item = QGraphicsPixmapItem()
        self.scene().addItem(self._item)
        self._has_image = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def set_document(self, document: ImageDocument) -> None:
        """Render a validated RGBA document without retaining mutable external buffers."""
        image = QImage(
            document.rgba_pixels,
            document.width,
            document.height,
            document.width * 4,
            QImage.Format.Format_RGBA8888,
        ).copy()
        self._item.setPixmap(QPixmap.fromImage(image))
        self.scene().setSceneRect(self._item.boundingRect())
        self._has_image = True
        self.reset_zoom()

    def clear_document(self) -> None:
        """Clear pixels and restore the default view transform."""
        self._item.setPixmap(QPixmap())
        self._has_image = False
        self.resetTransform()

    def reset_zoom(self) -> None:
        """Fit the full source into the viewport while preserving aspect ratio."""
        self.resetTransform()
        if self._has_image:
            self.fitInView(self._item, Qt.AspectRatioMode.KeepAspectRatio)

    def zoom_in(self) -> None:
        """Increase preview scale within a safe bound."""
        self._scale_by(1.25)

    def zoom_out(self) -> None:
        """Decrease preview scale within a safe bound."""
        self._scale_by(0.8)

    def _scale_by(self, factor: float) -> None:
        if not self._has_image:
            return
        current = self.transform().m11()
        target = current * factor
        if self.MIN_SCALE <= target <= self.MAX_SCALE:
            self.scale(factor, factor)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Zoom with the mouse wheel when a source is visible."""
        if not self._has_image:
            super().wheelEvent(event)
            return
        self._scale_by(1.15 if event.angleDelta().y() > 0 else 1 / 1.15)
        event.accept()
