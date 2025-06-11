from typing import Any

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QGraphicsItem

from conf import REFRESH_OBJ_TIMEOUT
from graphic.ZoomableView import ZoomableView
from graphic.items import RectangleItem
from optics.MirrorController import MirrorController
from render.Laser import Laser


class Mirror(RectangleItem):
    def __init__(self, x: float, y: float, width: float, height: float, view: ZoomableView):
        super().__init__(x, y, width, height, view)
        self.controller = MirrorController(self.center_pos().x(), self.center_pos().y(), width, height)

        self._timer_active = False
        view.scene().addItem(self)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange or change == QGraphicsItem.GraphicsItemChange.ItemRotationChange:
            self.controller.pos = self.center_pos()
            self.controller.rotation = self.rotation()
            if not self._timer_active:
                self._timer_active = True
                QTimer.singleShot(REFRESH_OBJ_TIMEOUT, lambda: ([self.controller.update_props(), Laser.recalc_all()],
                                                            setattr(self, '_timer_active', False)))


        return super().itemChange(change, value)
