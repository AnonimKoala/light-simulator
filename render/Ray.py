from PyQt6.QtCore import QPointF

from graphic.base import ZoomableView
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
        for i, segment, in enumerate(path):
            path[i] = {"start": QPointF(segment["start"].x, segment["start"].y), "end": QPointF(segment["end"].x, segment["end"].y)}
        if path is None:
            self.path_points = []
        else:
            self.path_points = path
        self.rerender()
