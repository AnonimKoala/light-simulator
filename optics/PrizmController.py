from PyQt6.QtCore import QPointF

from optics.BasicObject import BasicObject
from optics.Solver import Solver


class PrizmController(BasicObject):
    def __init__(self, x: float, y: float, vertices: list[QPointF]):
        Solver.optical_objects.append(self)

    def get_collision(self, ray):
        pass
