from graphic.base import ZoomableView
from graphic.items import RayGraphicItem
from optics.RayController import RayController


class Ray(RayGraphicItem):
    def __init__(self, parent, end_point, view: ZoomableView):
        super().__init__(parent, end_point, view)
        self.controller =  RayController()

    def update_props(self):
        self.rerender()