from typing import Any

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QGraphicsItem
from sympy import Point2D

from conf import REFRESH_OBJ_TIMEOUT
from graphic.base import ZoomableView
from graphic.items import LenGraphicItem
from optics.LenController import LenController
from render.Laser import Laser


class Len(LenGraphicItem):
    def __init__(self, x: float, y: float, height: float, view: ZoomableView, left_radius: float,
                 right_radius: float, width: float = -1):
        if width < 0:
            width = abs(right_radius) + abs(left_radius)
        self.controller = LenController(x, y, width, height, left_radius, right_radius)
        self._timer_active = False
        super().__init__(x, y, width, height, view, left_radius, right_radius)
        self.scene().addItem(self)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange or change == QGraphicsItem.GraphicsItemChange.ItemRotationChange:
            self.controller.pos = Point2D(self.center_pos().x(), self.center_pos().y())
            self.controller.rotation = self.rotation()

            if not self._timer_active:
                self._timer_active = True
                QTimer.singleShot(REFRESH_OBJ_TIMEOUT, lambda: ([self.controller.update_props(), Laser.recalc_all()],
                                                                setattr(self, '_timer_active', False)))
        return super().itemChange(change, value)
