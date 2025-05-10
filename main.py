from PyQt6.QtWidgets import QApplication, QGraphicsScene
import sys

from graphic.base import ZoomableView
from graphic.config import SCENE_SIZE
from render.Laser import Laser
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

    mirror = Mirror(-100, -50, 20, 200, view)
    scene.addItem(mirror)

    laser = Laser(50, 50, 50, view)
    scene.addItem(laser)

    view.resize(800, 600)
    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
