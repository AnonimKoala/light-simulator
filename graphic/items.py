from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QLinearGradient, QColor, QBrush, QPen, QPainter, QPainterPath, QPolygonF
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsItem
from sympy import pi, cos, sin
from graphic.base import SceneItem, ZoomableView
from conf import RAY_MAX_LENGTH, RAY_PEN_WIDTH
from optics.util import round_point


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
        self.setBrush(QBrush(QColor("green")))
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
        view.scene().addItem(self)
        self.setPos(x, y)
        self.itemChange(QGraphicsItem.GraphicsItemChange.ItemPositionChange, QPointF(x,y))
        self._brush = QBrush(QColor(0, 128, 128))
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
        # Draw a small dot at the lens position (center)
        center_x = int(self.width / 2)
        center_y = int(self.height / 2)
        dot_radius = 3
        painter.setPen(QPen(QColor("blue"), 1))
        painter.setBrush(QBrush(QColor("blue")))
        painter.drawEllipse(center_x - dot_radius, center_y - dot_radius, dot_radius * 2, dot_radius * 2)
        # painter.drawRect(self.boundingRect())

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
        self.vertices = []

    def boundingRect(self) -> QRectF:
        # The bounding rectangle for the triangle
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        # Define the three points of the triangle (upright, filling the bounding rect)
        self.vertices = [
            QPointF(self.width / 2, self.height),  # Top center
            QPointF(self.width, 0),  # Bottom right
            QPointF(0, 0)  # Bottom left
        ]
        polygon = QPolygonF(self.vertices)
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawPolygon(polygon)


class RayGraphicItem(QGraphicsItem):
    """
    LineItem class represents a line shape in the scene.
    Inherits from QGraphicsItem.
    """

    def __init__(self, start_point: QPointF, view: ZoomableView, parent=None):
        """
        Initialize the LineItem.
        :param start_point: The starting point of the line.
        :param view: The ZoomableView that contains this item.
        :param parent: Laser, if the line is a direct ray from the laser
        :type parent: Laser | None
        """
        super().__init__()
        self._parent = parent
        self._start_point = start_point
        self.setZValue(1)
        self.pen_width = RAY_PEN_WIDTH
        self._inf_point = None
        self._path_points: list[dict[str, QPointF]] = []
        self.view = view
        self.view.scene().addItem(self)

    def __del__(self):
        try:
            if self._parent and hasattr(self._parent, "rays"):
                self._parent.rays.remove(self)
                if hasattr(self, "view") and self.view is not None:
                    scene = getattr(self.view, "scene", None)
                    if callable(scene):
                        s = scene()
                        if s is not None:
                            s.removeItem(self)
        except RuntimeError:
            pass

    def boundingRect(self):
        rect = QRectF(self.start_point, self.inf_point).normalized()
        return rect.adjusted(-self.pen_width, -self.pen_width, self.pen_width, self.pen_width)

    def paint(self, painter, option, widget=None):
        gradient = QLinearGradient(self.start_point, self.inf_point)
        gradient.setColorAt(0, QColor(255, 255, 0, 255))
        gradient.setColorAt(0.85, QColor(255, 255, 0, 255))
        gradient.setColorAt(1.0, QColor(255, 255, 0, 0))
        pen = QPen(QBrush(gradient), self.pen_width)
        if len(self.path_points) > 0:
            current_pen_alpha = 55
            painter.setPen(QPen(QColor(255, 155, 0, current_pen_alpha), self.pen_width))
            print(self.path_points)
            for i, point in enumerate(self.path_points):
                pen_alpha = point.get("alpha_color", 255)
                if pen_alpha != current_pen_alpha:
                    current_pen_alpha = pen_alpha
                    pen.setColor(QColor(255, 0, 0, current_pen_alpha))
                    painter.setPen(pen)
                painter.drawLine(self.path_points[i].get("start"), self.path_points[i].get("end"))
        else:
            painter.setPen(pen)
            painter.drawLine(self.start_point, self.inf_point)

    def rerender(self):
        self.scene().update()
        self.prepareGeometryChange()
        self.update()

    @property
    def path_points(self):
        return self._path_points

    @path_points.setter
    def path_points(self, value):
        self._path_points = value
        self.rerender()

    @property
    def start_point(self):
        if not self.parent:
            return round_point(self._start_point)
        return round_point(self.parent.source_point)

    @property
    def inf_point(self):
        if self._inf_point is not None:
            return self._inf_point
        end_x = self.start_point.x() + RAY_MAX_LENGTH * cos(self.angle_rad)
        end_y = self.start_point.y() + RAY_MAX_LENGTH * sin(self.angle_rad)
        return QPointF(end_x, end_y)

    @inf_point.setter
    def inf_point(self, value):
        self._inf_point = value
        self.rerender()

    @property
    def parent(self):
        return self._parent

    @property
    def angle_deg(self):
        return int(self.parent.rotation() if self.parent else 0)

    @property
    def angle_rad(self):
        return int(self.angle_deg * pi / 180)
