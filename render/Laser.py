from typing import Any
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QGraphicsItem
from graphic.base import ZoomableView
from graphic.items import RectangleItem
from render.Ray import Ray


class Laser(RectangleItem):
    def __init__(self, x: float, y: float, size: float, view: ZoomableView):
        super().__init__(x, y, size * 2, size, view)
        self.setBrush(QBrush(QColor("purple")))
        self.setZValue(2)
        self.rays = [
            Ray(self.source_point, view, self),
        ]

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange or change == QGraphicsItem.GraphicsItemChange.ItemRotationChange:
            for ray in self.rays:
                ray.update_props()
        return super().itemChange(change, value)

    @property
    def source_point(self):
        right_center_local = QPointF(self.rect().right(), self.rect().center().y())
        return self.mapToScene(right_center_local)
