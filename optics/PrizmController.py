from PyQt6.QtCore import QPointF

from optics.BasicObject import BasicObject


class PrizmController(BasicObject):
    def __init__(self, x: float, y: float, vertices: list[QPointF]):
        pass

    def get_collision_point(self, ray):
        pass
