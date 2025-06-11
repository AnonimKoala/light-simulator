from PyQt6.QtWidgets import QApplication, QGraphicsScene
import sys

from graphic.ZoomableView import ZoomableView
from graphic.config import SCENE_SIZE
from render.Laser import Laser
from render.Len import Len
from render.Mirror import Mirror


def main():
    app = QApplication(sys.argv)

    # Create a graphics scene
    scene = QGraphicsScene()
    scene.setSceneRect(-SCENE_SIZE / 2, -SCENE_SIZE / 2, SCENE_SIZE, SCENE_SIZE)  # Define coordinate bounds

    view = ZoomableView(scene)   # Create a zoomable view and set the scene
    view.scale(1, -1)        # Invert the y-axis for correct orientation
    view.setWindowTitle("Light Simulator")

    ###################################################################
    # Place your objects here
    # Example objects can be added to the scene
    # Uncomment the following lines to add objects to the scene

    # Mirror(100,50, 20,200, view)
    # Len(0, 10, 200, view, -30, 30)
    # Laser(50, 50, 50, view)

    Mirror(0,0, 20,200, view)
    Laser(150, 50, 50, view)

    ###################################################################

    view.resize(800, 600)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
