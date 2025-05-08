from PyQt6.QtCore import QPointF
from sympy import Point2D, cos, sin, Segment2D
from .BasicObject import BasicObject
from .Material import Material
from .RayController import RayController
from .Solver import Solver


class MirrorController(BasicObject):
    """
    The `Mirror` class allows the creation of mirrors.
    """

    DEF_WIDTH = 20
    DEF_HEIGHT = 60

    def __init__(self, x: float, y: float, width: float = DEF_WIDTH, height: float = DEF_HEIGHT):
        """
        Initializes an instance of the `Mirror` class.

        :param x: X-coordinate of the center
        :param y: Y-coordinate of the center
        :param width: Width of the mirror
        :param height: Height of the mirror
        """
        self._pos = Point2D(x, y)
        self.width = width
        self.height = height
        self._rotation = 0
        self.material = Material(100, 10000)
        Solver.optical_objects.append(self)

    def get_collision(self, ray: RayController) -> Point2D | None:
        intersections = []
        for side in self.sides.values():
            if intersection_point := ray.first_intersection(side):
                intersections.append(intersection_point)
        if intersections:
            return Solver.nearest_to_origin(ray.start_point, intersections)
        return None

    @property
    def pos(self) -> Point2D:
        return self._pos

    @pos.setter
    def pos(self, value: Point2D | QPointF):
        if isinstance(value, QPointF):
            value = Point2D(value.x(), value.y())
        self._pos = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value: float):
        self._rotation = value

    @property
    def vertices(self):
        width2cos = (self.width / 2) * cos(self.rotation)
        width2sin = (self.width / 2) * sin(self.rotation)
        height2cos = (self.height / 2) * cos(self.rotation)
        height2sin = (self.height / 2) * sin(self.rotation)
        return {
            "top-left": Point2D(self.pos.x - width2cos - height2sin, self.pos.y - width2sin + height2cos),
            "top-right": Point2D(self.pos.x + width2cos - height2sin, self.pos.y + width2sin + height2cos),
            "bottom-right": Point2D(self.pos.x + width2cos + height2sin, self.pos.y + width2sin - height2cos),
            "bottom-left": Point2D(self.pos.x - width2cos + height2sin, self.pos.y - width2sin - height2cos),
        }

    @property
    def sides(self):
        vertices = self.vertices
        return {
            "left": Segment2D(vertices["top-left"], vertices["bottom-left"]),
            "right": Segment2D(vertices["top-right"], vertices["bottom-right"]),
            "top": Segment2D(vertices["top-left"], vertices["top-right"]),
            "bottom": Segment2D(vertices["bottom-left"], vertices["bottom-right"]),
        }
