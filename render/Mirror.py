from typing import Any
from PyQt6.QtWidgets import QGraphicsItem
from graphic.base import ZoomableView
from graphic.items import RectangleItem
from optics.MirrorController import MirrorController
from render.Laser import Laser


class Mirror(RectangleItem):
    def __init__(self, x: float, y: float, width: float, height: float, view: ZoomableView):
        super().__init__(x, y, width, height, view)
        self.controller = MirrorController(self.center_pos().x(), self.center_pos().y(), width, height)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange or change == QGraphicsItem.GraphicsItemChange.ItemRotationChange:
            self.controller.pos = self.center_pos()
            self.controller.rotation = self.rotation()
            Laser.recalc_all()
        return super().itemChange(change, value)
