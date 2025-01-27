from PyQt6.QtGui import QLinearGradient, QColor, QBrush, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem

from graphic.base import SceneItem


class EllipseItem(QGraphicsEllipseItem, SceneItem):
    """Ellipse item with shared functionality from SceneItem."""

    def __init__(self, x, y, width, height, view):
        QGraphicsEllipseItem.__init__(self, 0, 0, width, height)
        SceneItem.__init__(self, x, y, width, height, view)

        # Define a linear gradient in local coordinates
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0.0, QColor("red"))
        gradient.setColorAt(1.0, QColor("green"))

        self.setBrush(QBrush(gradient))
        self.setPen(QPen(QColor("white")))


class RectangleItem(QGraphicsRectItem, SceneItem):
    def __init__(self, x, y, width, height, view):
        QGraphicsRectItem.__init__(self, 0, 0, width, height)
        SceneItem.__init__(self, x, y, width, height, view)

        # Set appearance
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0.0, QColor(0, 0, 255))  # Blue
        gradient.setColorAt(1.0, QColor(0, 255, 255))  # Cyan

        self.setBrush(QBrush(gradient))
        self.setPen(QPen(QColor("white")))


