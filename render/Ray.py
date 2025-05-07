from PyQt6.QtCore import QPointF

from graphic.base import ZoomableView
from graphic.items import RayGraphicItem
from optics.RayController import RayController


class Ray(RayGraphicItem):
    def __init__(self, start_point: QPointF, view: ZoomableView, parent=None):
        super().__init__(start_point, view, parent)
        self.controller = RayController(start_point)

    def __del__(self):
        del self.controller
        super().__del__()

    def update_props(self):
        self.controller.update_props(self.start_point, self.angle_deg)
        refractions = self.controller.get_refractions()
        if refractions is None:
            self.path_points = []
        else:
            self.path_points = [
                self.start_point,
                *refractions,
                self.inf_point
            ]
        self.rerender()
