from PyQt6.QtCore import QPointF
from sympy import Point2D, cos, sin, Segment2D, Ray
from .BasicController import BasicController
from .Material import Material
from .Solver import Solver
from .util import deg2rad, round_point, round_segment, round_line, is_point_inside_polygon


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
        self._vertices = {}
        self._sides = {}
        self.material: Material = Material.glass()
        self.update_props()
        Solver.optical_objects.append(self)

    def get_collision(self, ray: Ray) -> dict[str, Point2D | Segment2D | Material | bool] | None:
        intersections = []
        for side in self.sides.values():
            if intersection_point := Solver.first_intersection(ray,side):
                intersections.append({"point": round_point(intersection_point), "side": side})
        intersections = [cp for cp in intersections if cp["point"] != round_point(ray.source)]
        if intersections:
            closest_intersection = min(intersections, key=lambda cp: cp["point"].distance(ray.source))
            return {
                "surface": closest_intersection["side"],
                "point": closest_intersection["point"],
                "normal": round_line(closest_intersection["side"].perpendicular_line(closest_intersection["point"])),
                "material": self.material,
                "is-from-inside": self.is_point_inside(ray.source),
                "thickness": self.width/100 # Assuming thickness [m] is the width of the mirror,
            }
        return None

    def is_point_inside(self, point: Point2D | QPointF) -> bool:
        """
        Checks if a point is inside the mirror's area.

        :param point: The point to check
        :type point: Point2D or QPointF
        :return: True if the point is inside, False otherwise
        """
        if isinstance(point, QPointF):
            point = Point2D(point.x(), point.y())
        polygon = [
            self.vertices["top-left"],
            self.vertices["top-right"],
            self.vertices["bottom-right"],
            self.vertices["bottom-left"]
        ]
        return is_point_inside_polygon(point, polygon)

    def update_props(self):
        """
        Updates the properties of the mirror, recalculating its props
        """
        self.calc_vertices()
        self.calc_sides()

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
        return self._vertices

    def calc_vertices(self):
        width2cos = (self.width / 2) * cos(deg2rad(self.rotation))
        width2sin = (self.width / 2) * sin(deg2rad(self.rotation))
        height2cos = (self.height / 2) * cos(deg2rad(self.rotation))
        height2sin = (self.height / 2) * sin(deg2rad(self.rotation))
        self._vertices = {
            "top-left": round_point(Point2D(self.pos.x - width2cos - height2sin, self.pos.y - width2sin + height2cos)),
            "top-right": round_point(Point2D(self.pos.x + width2cos - height2sin, self.pos.y + width2sin + height2cos)),
            "bottom-right": round_point(Point2D(self.pos.x + width2cos + height2sin, self.pos.y + width2sin - height2cos)),
            "bottom-left": round_point(Point2D(self.pos.x - width2cos + height2sin, self.pos.y - width2sin - height2cos)),
        }

    @property
    def sides(self):
        return self._sides

    def calc_sides(self):
        vertices = self.vertices
        self._sides = {
            "left": round_segment(Segment2D(vertices["top-left"], vertices["bottom-left"])),
            "right": round_segment(Segment2D(vertices["top-right"], vertices["bottom-right"])),
            "top": round_segment(Segment2D(vertices["top-left"], vertices["top-right"])),
            "bottom": round_segment(Segment2D(vertices["bottom-left"], vertices["bottom-right"])),
        }
