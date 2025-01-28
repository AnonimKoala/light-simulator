from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QLinearGradient, QColor, QBrush, QPen, QPainterPath
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPathItem

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


class CustomShapeItem(QGraphicsPathItem, SceneItem):
    """Custom shape item: Rectangle with half-width cut by an ellipse."""

    def __init__(self, x, y, width, height, view):
        # Initialize parent classes
        QGraphicsPathItem.__init__(self)
        SceneItem.__init__(self, x, y, width, height, view)
        self.setPos(x,y)

        # Store initial dimensions
        self.original_width = width
        self.original_height = height

        # Initialize dimensions
        self.width = width
        self.height = height

        # Create the custom shape
        self.update_path(width, height)

        # Set appearance (blue gradient)
        self.setBrush(QBrush(QColor(0, 0, 255)))  # Solid blue color
        self.setPen(QPen(QColor("white")))  # White outline for visibility

    def update_path(self, width, height):
        """Update the path based on the current width and height."""
        rect_path = QPainterPath()
        rect_path.addRect(0, 0, width, height)  # Rectangle path

        ellipse_path = QPainterPath()
        ellipse_path.addEllipse(-width / 2, 0, width, height)  # Ellipse path

        # Subtract the ellipse from the rectangle
        final_path = rect_path.subtracted(ellipse_path)

        self.setPath(final_path)

    def setRect(self, x, y, width, height):
        """Override setRect to update custom shape dimensions."""
        self.prepareGeometryChange()

        # Update position and dimensions
        self.setPos(x, y)
        self.update_path(width, height)

        # Update internal size attributes for compatibility with SceneItem
        self.width = width
        self.height = height

    def rect(self):
        """Return the bounding rectangle of the custom shape."""
        return QRectF(0, 0, self.width, self.height)