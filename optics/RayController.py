from PyQt6.QtCore import QPointF
from sympy import Point2D, pi, Ray as SympyRay

from optics.Solver import Solver


class RayController:

    def __init__(self, start_point: QPointF):
        super().__init__()
        self._start_point = Point2D(start_point.x(), start_point.y())
        self._end_point = None
        self._angle_deg = 0.0
        self.ray = None

    def update_props(self, start_point: QPointF, angle_deg: float):
        self.start_point = Point2D(start_point.x(), start_point.y())
        self.angle_deg = angle_deg
        self.ray = SympyRay(self.start_point, angle=self.angle_rad)

    def get_refractions(self) -> list[QPointF] | None:
        Solver.collision_detector(self)

    @property
    def start_point(self):
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
