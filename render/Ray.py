from PyQt6.QtCore import QPointF

from graphic.ZoomableView import ZoomableView
from graphic.items import RayGraphicItem
from optics.RayController import RayController
from optics.Solver import Solver


class Ray(RayGraphicItem):
    def __init__(self, start_point: QPointF, view: ZoomableView, parent=None):
        super().__init__(start_point, view, parent)
        self.controller = RayController(start_point)

    def __del__(self):
        del self.controller
        super().__del__()

    def update_props(self):
        self.controller.update_props(self.start_point, self.angle_deg)
        self.calc()

    def calc(self):
        path = Solver.get_path(self.controller.ray)
        self.path_points = []
        for i, data, in enumerate(path):
            self.path_points.append({"start": QPointF(data["start"].x, data["start"].y), "end": QPointF(data["end"].x, data["end"].y), "alpha_color": int(data["alpha_color"])})
        self.rerender()
