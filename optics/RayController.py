from PyQt6.QtCore import QPointF
from sympy import Point2D, pi, Ray as SympyRay

from optics.Solver import Solver


class RayController:

    def __init__(self, start_point: QPointF):
        super().__init__()
        self._start_point = Point2D(start_point.x(), start_point.y())
        self._end_point = None
        self._angle_deg = 0.0
        self.ray = SympyRay(self.start_point, angle=self.angle_rad)

    def update_props(self, start_point: QPointF, angle_deg: float):
        self.start_point = Point2D(start_point.x(), start_point.y())
        self.angle_deg = angle_deg
        self.ray = SympyRay(self.start_point, angle=self.angle_rad)

    def get_refractions(self) -> Point2D | None:
        ox = Line2D(Point2D(0, 0), Point2D(1, 0))
        # new_angle =
        if collision := Solver.find_first_collision(self):
            surface_angle = ox.smallest_angle_between(collision["surface"])
            beta = 2 * surface_angle - ox.smallest_angle_between(self.ray)
            incidence_angle = 90 - beta
            SympyRay(collision["point"],  angle=beta+surface_angle)
            print("beta", rad2deg(beta).evalf())

            return Solver.find_first_collision(self)["point"]
        return None

    def first_intersection(self, obj) -> Point2D | None:
        if intersections := self.ray.intersection(obj):
            return Solver.nearest_to_origin(self.start_point, intersections)
        return None

    def intersections(self, obj):
        """ Finds all intersections of the ray with the given object. """
        if intersections := self.ray.intersection(obj):
            return intersections
        return None

    def distance(self, obj):
        return self.ray.distance(obj)

    @property
    def start_point(self) -> Point2D:
        return self._start_point

    @start_point.setter
    def start_point(self, value):
        self._start_point = value

    @property
    def angle_deg(self):
        return self._angle_deg

    @angle_deg.setter
    def angle_deg(self, value):
        self._angle_deg = value

    @property
    def angle_rad(self):
        return self.angle_deg * pi / 180.0
