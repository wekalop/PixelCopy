"""DPI-aware virtual-desktop screen capture."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter


def virtual_desktop_geometry() -> QRect:
    """Return the union of all active monitor geometries, including negative origins."""
    geometry = QRect()
    for screen in QGuiApplication.screens():
        geometry = geometry.united(screen.geometry())
    return geometry


def logical_to_physical_rect(rect: QRect, screen_rect: QRect, scale: float) -> QRect:
    """Map a logical intersection to physical pixels relative to one monitor."""
    relative = rect.translated(-screen_rect.topLeft())
    return QRect(
        round(relative.x() * scale),
        round(relative.y() * scale),
        round(relative.width() * scale),
        round(relative.height() * scale),
    )


class ScreenshotService:
    """Capture a logical virtual-desktop region into physical pixels."""

    def capture_region(self, selection: QRect) -> QImage:
        normalized = selection.normalized()
        if normalized.width() < 3 or normalized.height() < 3:
            raise ValueError("Select a region at least 3 by 3 pixels.")
        intersections = [
            (screen, normalized.intersected(screen.geometry()))
            for screen in QGuiApplication.screens()
            if normalized.intersects(screen.geometry())
        ]
        if not intersections:
            raise ValueError("The selected region is outside the active displays.")

        output_scale = max(screen.devicePixelRatio() for screen, _ in intersections)
        output = QImage(
            QSize(
                max(1, round(normalized.width() * output_scale)),
                max(1, round(normalized.height() * output_scale)),
            ),
            QImage.Format.Format_RGBA8888,
        )
        output.fill(Qt.GlobalColor.transparent)
        painter = QPainter(output)
        try:
            for screen, intersection in intersections:
                screenshot = screen.grabWindow(0).toImage()
                scale = screen.devicePixelRatio()
                source = logical_to_physical_rect(intersection, screen.geometry(), scale)
                target_origin = QPoint(
                    round((intersection.x() - normalized.x()) * output_scale),
                    round((intersection.y() - normalized.y()) * output_scale),
                )
                target = QRect(
                    target_origin,
                    QSize(
                        round(intersection.width() * output_scale),
                        round(intersection.height() * output_scale),
                    ),
                )
                painter.drawImage(target, screenshot, source)
        finally:
            painter.end()
        return output
