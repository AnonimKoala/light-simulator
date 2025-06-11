from typing import Any
from PyQt6.QtCore import QPointF, QTimer
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QGraphicsItem
from conf import REFRESH_LASER_TIMEOUT
from graphic.ZoomableView import ZoomableView
from graphic.items import RectangleItem
from optics.Solver import Solver
from render.Ray import Ray


class Laser(RectangleItem):
    _all_timer_active = False

    @staticmethod
    def recalc_all():
        if not Laser._all_timer_active:
            Laser._all_timer_active = True
            for laser in Solver.lasers:
                QTimer.singleShot(REFRESH_LASER_TIMEOUT, lambda: ([ray.calc() for ray in laser.rays],
                                                                  setattr(Laser, '_all_timer_active', False)))

    def __init__(self, x: float, y: float, size: float, view: ZoomableView):
        super().__init__(x, y, size * 2, size, view)
        self.setBrush(QBrush(QColor("purple")))
        self.setZValue(2)
        self.rays = [
            Ray(self.source_point, view, self),
        ]
        Solver.lasers.append(self)
        self._timer_active = False
        view.scene().addItem(self)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange or change == QGraphicsItem.GraphicsItemChange.ItemRotationChange:
            if not self._timer_active:
                self._timer_active = True
                QTimer.singleShot(REFRESH_LASER_TIMEOUT, lambda: ([ray.update_props() for ray in self.rays],
                                                                  setattr(self, '_timer_active', False)))

        return super().itemChange(change, value)

    @property
    def source_point(self):
        right_center_local = QPointF(self.rect().right(), self.rect().center().y())
        return self.mapToScene(right_center_local)
