from typing import Any

from PyQt6.QtWidgets import QGraphicsItem
from sympy import Point2D

from graphic.base import ZoomableView
from graphic.items import LenGraphicItem
from optics.LenOpticsController import LenOpticsController


class Len(LenGraphicItem):
    def __init__(self, x: float, y: float, width: float, height: float, view: ZoomableView, left_radius: float, right_radius: float):
        self.controller = LenOpticsController(x, y)
        super().__init__(x, y, width, height, view, left_radius, right_radius)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            self.controller.pos = Point2D(self.pos().x(), self.pos().y())
        return super().itemChange(change, value)



