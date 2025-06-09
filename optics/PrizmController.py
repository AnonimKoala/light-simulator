from PyQt6.QtCore import QPointF

from optics.BasicController import BasicController
from optics.Solver import Solver


class PrizmController(BasicController):
    def __init__(self, x: float, y: float, vertices: list[QPointF]):
        Solver.optical_objects.append(self)

    def get_collision(self, ray):
        pass
