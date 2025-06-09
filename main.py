from PyQt6.QtWidgets import QApplication, QGraphicsScene
import sys

from graphic.base import ZoomableView
from graphic.config import SCENE_SIZE
from render.Laser import Laser
from render.Len import Len
from render.Mirror import Mirror


def main():
    app = QApplication(sys.argv)

    # Create a graphics scene
    scene = QGraphicsScene()
    scene.setSceneRect(-SCENE_SIZE / 2, -SCENE_SIZE / 2, SCENE_SIZE, SCENE_SIZE)  # Define coordinate bounds

    # Create a zoomable view and set the scene
    view = ZoomableView(scene)
    view.scale(1, -1)
    view.setWindowTitle("Light Simulator")

    len_obj = Len(0, 10, 60, 200, view, -30, 30)
    scene.addItem(len_obj)

    # m = Mirror(0,0, 20,200, view)
    # scene.addItem(m)
    # m2 = Mirror(-100,0, 20,200, view)
    # scene.addItem(m2)

    laser = Laser(50, 50, 50, view)
    scene.addItem(laser)

    view.resize(800, 600)
    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
