from PyQt6.QtGui import QLinearGradient, QColor, QBrush, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem

from graphic.base import SceneItem, ZoomableView


class EllipseItem(QGraphicsEllipseItem, SceneItem):
    """
    EllipseItem class represents an ellipse shape in the scene.
    Inherits from QGraphicsEllipseItem and SceneItem.
    """

    def __init__(self, x: float, y: float, width: float, height: float, view: ZoomableView):
        """
        Initialize the EllipseItem.

        :param x: float - X-coordinate of the ellipse.
        :param y: float - Y-coordinate of the ellipse.
        :param width: float - Width of the ellipse.
        :param height: float - Height of the ellipse.
        :param view: ZoomableView - The ZoomableView that contains this item.
        """
        QGraphicsEllipseItem.__init__(self, 0, 0, width, height)
        SceneItem.__init__(self, x, y, width, height, view)

        # Define a linear gradient in local coordinates
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0.0, QColor("red"))
        gradient.setColorAt(1.0, QColor("green"))

        self.setBrush(QBrush(gradient))
        self.setPen(QPen(QColor("white")))


class RectangleItem(QGraphicsRectItem, SceneItem):
    """
    RectangleItem class represents a rectangle shape in the scene.
    Inherits from QGraphicsRectItem and SceneItem.
    """

    def __init__(self, x: float, y: float, width: float, height: float, view: ZoomableView):
        """
        Initialize the RectangleItem.

        :param x: float - X-coordinate of the rectangle.
        :param y: float - Y-coordinate of the rectangle.
        :param width: float - Width of the rectangle.
        :param height: float - Height of the rectangle.
        :param view: ZoomableView - The ZoomableView that contains this item.
        """
        QGraphicsRectItem.__init__(self, 0, 0, width, height)
        SceneItem.__init__(self, x, y, width, height, view)

        # Set appearance
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0.0, QColor(0, 0, 255))  # Blue
        gradient.setColorAt(1.0, QColor(0, 255, 255))  # Cyan

        self.setBrush(QBrush(gradient))
        self.setPen(QPen(QColor("white")))