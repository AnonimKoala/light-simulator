from PyQt6.QtWidgets import QApplication, QGraphicsScene
import sys

from graphic.base import ZoomableView, SceneItem
from graphic.config import SCENE_SIZE
from graphic.items import EllipseItem, RectangleItem


def main():
    app = QApplication(sys.argv)

    # Create a graphics scene
    scene = QGraphicsScene()
    scene.setSceneRect(-SCENE_SIZE / 2, -SCENE_SIZE / 2, SCENE_SIZE, SCENE_SIZE)  # Define coordinate bounds

    # Create a zoomable view and set the scene
    view = ZoomableView(scene)
    view.scale(1, -1)
    view.setWindowTitle("Light Simulator")

    ellipse1 = EllipseItem(-100, -50, 200, 100, view)
    ellipse2 = EllipseItem(200, 200, 150, 75, view)
    scene.addItem(ellipse1)
    scene.addItem(ellipse2)

    rectangle = RectangleItem(50, 50, 150, 100, view)
    scene.addItem(rectangle)

    view.resize(800, 600)
    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
