from sympy import sqrt

from graphic.ZoomableView import ZoomableView
from graphic.items import TriangleItem
from optics.PrizmController import PrizmController


class Prizm(TriangleItem):
    def __init__(self, x: float, y: float, side: float, view: ZoomableView):
        super().__init__(x, y, side, (side * sqrt(3)) / 2, view)
        self.controller = PrizmController(x, y, self.vertices)
