from PyQt6.QtCore import QPointF

from graphic.base import ZoomableView
from graphic.items import RayGraphicItem
from optics.RayController import RayController


class Ray(RayGraphicItem):
    def __init__(self, start_point: QPointF, view: ZoomableView, parent=None):
        super().__init__(start_point, view, parent)
        self.controller =  RayController()

    def update_props(self):
        self.rerender()