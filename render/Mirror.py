from graphic.base import ZoomableView
from graphic.items import RectangleItem
from optics.MirrorOpticsController import MirrorOpticsController


class Mirror(RectangleItem):
    def __init__(self, x: float, y: float, width: float, height: float, view: ZoomableView):
        super().__init__(x, y, width, height, view)
        self.controller = MirrorOpticsController(x, y, width, height)
