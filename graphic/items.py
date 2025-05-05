from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QLinearGradient, QColor, QBrush, QPen, QPainter, QPainterPath, QPolygonF
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


class LenGraphicItem(SceneItem):
    """
    LenGraphicItem class represents a lens-shaped item in the scene. Inherits from SceneItem.
    This class creates a graphical representation of a lens with customizable
    left and right radii. Positive radius values create convex curves,
    while negative values create concave curves.
    """

    def __init__(self, x: float, y: float, width: float, height: float, view: ZoomableView, left_radius: float,
                 right_radius: float):
        SceneItem.__init__(self, x, y, width, height, view)
        self.setPos(x, y)
        self._brush = QBrush(QColor(0, 128, 128))
        self._pen = QPen(QColor("white"))
        self.left_radius = left_radius
        self.right_radius = right_radius

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None):
        # Calculate the starting x position and width of the central rectangle,
        # adjusting for positive left and right radii (convex lens sides).
        rect_x, rect_width = 0, self.width

        if self.right_radius > 0:
            rect_width -= self.right_radius
        if self.left_radius > 0:
            rect_x = self.left_radius
            rect_width -= self.left_radius

        # Create a rectangle path representing the lens's body area.
        rect = QRectF(rect_x, 0, rect_width, self.height)
        path = QPainterPath()
        path.addRect(rect)

        # Handle the right side of the lens:
        # - If right_radius < 0, subtract a concave half-ellipse from the right.
        # - If right_radius > 0, add a convex half-ellipse to the right.
        if self.right_radius < 0:
            ellipse_x = self.width + self.right_radius
            ellipse_rect = QRectF(ellipse_x, 0, self.right_radius * -2, self.height)
            half_ellipse = QPainterPath()
            half_ellipse.moveTo(ellipse_x - self.right_radius, self.height)
            half_ellipse.arcTo(ellipse_rect, 90, 180)
            path = path.subtracted(half_ellipse)
        elif self.right_radius > 0:
            ellipse_x = self.width - 2 * self.right_radius
            ellipse_rect = QRectF(ellipse_x, 0, self.right_radius * 2, self.height)
            half_ellipse = QPainterPath()
            half_ellipse.moveTo(ellipse_x + self.right_radius, self.height)
            half_ellipse.arcTo(ellipse_rect, 90, -180)
            path = path.united(half_ellipse)

        # Handle the left side of the lens:
        # - If left_radius < 0, subtract a concave half-ellipse from the left.
        # - If left_radius > 0, add a convex half-ellipse to the left.
        if self.left_radius < 0:
            ellipse_x = 0
            ellipse_rect = QRectF(ellipse_x + self.left_radius, 0, self.left_radius * -2, self.height)
            half_ellipse = QPainterPath()
            half_ellipse.moveTo(ellipse_x, self.height)
            half_ellipse.arcTo(ellipse_rect, 90, -180)
            path = path.subtracted(half_ellipse)
        elif self.left_radius > 0:
            ellipse_x = -self.left_radius
            ellipse_rect = QRectF(ellipse_x + self.left_radius, 0, self.left_radius * 2, self.height)
            half_ellipse = QPainterPath()
            half_ellipse.moveTo(ellipse_x + 2 * self.left_radius, self.height)
            half_ellipse.arcTo(ellipse_rect, 90, 180)
            path = path.united(half_ellipse)

        # Draw the final lens shape with no outline and the current brush.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.brush())
        painter.drawPath(path)

    def brush(self):
        return getattr(self, "_brush", QBrush(QColor(0, 128, 128)))


class TriangleItem(SceneItem):
    """
    TriangleItem class represents a triangle shape in the scene.
    Inherits from QGraphicsItem and SceneItem.
    """
    def __init__(self, x: float, y: float, width: float, height: float, view: ZoomableView):
        SceneItem.__init__(self, x, y, width, height, view)
        self.setPos(x, y)
        self._brush = QBrush(QColor("orange"))
        self._pen = QPen(QColor("white"))

    def boundingRect(self) -> QRectF:
        # The bounding rectangle for the triangle
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        # Define the three points of the triangle (upright, filling the bounding rect)
        points = [
            QPointF(self.width / 2, 0),               # Top center
            QPointF(self.width, self.height),         # Bottom right
            QPointF(0, self.height)                   # Bottom left
        ]
        polygon = QPolygonF(points)
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawPolygon(polygon)
