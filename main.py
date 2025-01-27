from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsEllipseItem
from PyQt6.QtGui import QPen, QBrush, QLinearGradient, QColor
import sys

from graphic.base import ZoomableView, SceneItem
from graphic.config import SCENE_SIZE


class EllipseItem(QGraphicsEllipseItem, SceneItem):
    """Ellipse item with shared functionality from SceneItem."""

    def __init__(self, x, y, width, height, view):
        QGraphicsEllipseItem.__init__(self, 0, 0, width, height)
        SceneItem.__init__(self, x, y, width, height, view)

        # Define a linear gradient in local coordinates
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0.0, QColor("red"))
        gradient.setColorAt(1.0, QColor("green"))

        # Apply the gradient as a brush
        self.setBrush(QBrush(gradient))

        # Set a white pen for the outline
        self.setPen(QPen(QColor("white")))



def main():
    app = QApplication(sys.argv)

    # Create a graphics scene
    scene = QGraphicsScene()
    scene.setSceneRect(-SCENE_SIZE / 2, -SCENE_SIZE / 2, SCENE_SIZE, SCENE_SIZE)  # Define coordinate bounds

    # Create a zoomable view and set the scene
    view = ZoomableView(scene)
    view.setWindowTitle("Light Simulator")

    ellipse1 = EllipseItem(-100, -50, 200, 100, view)
    ellipse2 = EllipseItem(200, 200, 150, 75, view)
    scene.addItem(ellipse1)
    scene.addItem(ellipse2)

    view.resize(800, 600)
    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
