from PyQt6.QtCore import QPointF
from sympy import Point2D, cos, sin, Segment2D, Ray
from .BasicController import BasicController
from .Material import Material
from .RayController import RayController
from .Solver import Solver
from .util import round_and_float, deg2rad


class MirrorController(BasicController):
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

    def get_collision(self, ray: Ray) -> dict[str, Point2D | Segment2D] | None:
        intersections = []
        for side in self.sides.values():
            if intersection_point := Solver.first_intersection(ray,side):
                intersections.append({"point": intersection_point, "side": side})

        intersections = [cp for cp in intersections if cp["point"] != ray.source]
        if intersections:
            closest_intersection = min(intersections, key=lambda cp: cp["point"].distance(ray.source))
            return {
                "surface": closest_intersection["side"],
                "point": closest_intersection["point"],
                "normal": closest_intersection["side"].perpendicular_segment(closest_intersection["point"]),
            }
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
        width2cos = (self.width / 2) * cos(deg2rad(self.rotation))
        width2sin = (self.width / 2) * sin(deg2rad(self.rotation))
        height2cos = (self.height / 2) * cos(deg2rad(self.rotation))
        height2sin = (self.height / 2) * sin(deg2rad(self.rotation))
        return {
            "top-left": Point2D(round_and_float(self.pos.x - width2cos - height2sin), round_and_float(self.pos.y - width2sin + height2cos)),
            "top-right": Point2D(round_and_float(self.pos.x + width2cos - height2sin), round_and_float(self.pos.y + width2sin + height2cos)),
            "bottom-right": Point2D(round_and_float(self.pos.x + width2cos + height2sin), round_and_float(self.pos.y + width2sin - height2cos)),
            "bottom-left": Point2D(round_and_float(self.pos.x - width2cos + height2sin), round_and_float(self.pos.y - width2sin - height2cos)),
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
