from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem
from PyQt6.QtGui import QPainter, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF, QPointF
import sys

SCENE_SIZE = 5000


class ScalePoint(QGraphicsEllipseItem):
    """A small draggable point used for scaling."""

    def __init__(self, x, y, parent_item, opposite_point=None, direction=None):
        super().__init__(x - 5, y - 5, 10, 10)  # Create a small circle
        self.setBrush(QBrush(Qt.GlobalColor.red))  # Red color for scale points
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)  # Enable dragging
        self.parent_item = parent_item  # Reference to the parent item (scalable object)
        self.opposite_point = opposite_point  # The fixed point during scaling
        self.direction = direction  # Direction for scaling (horizontal/vertical)
        self.setZValue(2)  # Ensure scale points are always on top

    def mouseMoveEvent(self, event):
        """Handle dragging of the scale point to resize the parent item."""
        if not self.parent_item.scene().views()[0].scale_mode:
            return

        current_pos = event.scenePos()
        rect = self.parent_item.rect()

        if self.direction == "horizontal":
            # Get the opposite horizontal point as fixed point
            if current_pos.x() > rect.center().x():
                fixed_x = rect.left()  # If dragging right point, left is fixed
                new_width = (current_pos.x() - fixed_x)
                new_x = fixed_x
            else:
                fixed_x = rect.right()  # If dragging left point, right is fixed
                new_width = (fixed_x - current_pos.x())
                new_x = current_pos.x()
            self.parent_item.setRect(new_x, rect.top(), new_width, rect.height())

        elif self.direction == "vertical":
            # Get the opposite vertical point as fixed point
            if current_pos.y() > rect.center().y():
                fixed_y = rect.top()  # If dragging bottom point, top is fixed
                new_height = (current_pos.y() - fixed_y)
                new_y = fixed_y
            else:
                fixed_y = rect.bottom()  # If dragging top point, bottom is fixed
                new_height = (fixed_y - current_pos.y())
                new_y = current_pos.y()
            self.parent_item.setRect(rect.left(), new_y, rect.width(), new_height)

        else:
            # Default scaling (corner point)
            if self.opposite_point:  # Use opposite_point instead of opposite_corner
                new_width = abs(current_pos.x() - self.opposite_point.x())
                new_height = abs(current_pos.y() - self.opposite_point.y())
                new_x = min(current_pos.x(), self.opposite_point.x())
                new_y = min(current_pos.y(), self.opposite_point.y())
                self.parent_item.setRect(new_x, new_y, new_width, new_height)

        # Update positions of all scale points
        self.parent_item.update_scale_points()


class ZoomableView(QGraphicsView):
    """Zoomable view with panning and scalability toggling."""

    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)  # Enable panning

        self.scale_mode = False

    def hide_objs_scale_points(self):
        for item in self.scene().items():
            if isinstance(item, EllipseItem):
                item.hide_scale_points()

    def keyPressEvent(self, event):
        """Handle key press events for toggling scalability."""
        if event.key() == Qt.Key.Key_S:  # Press 'S' to toggle scale mode for selected items
            self.scale_mode = not self.scale_mode

            if self.scale_mode:
                selected_item = self.scene().selectedItems()[0]
                if isinstance(selected_item, EllipseItem):
                    selected_item.show_scale_points()
            else:
                self.hide_objs_scale_points()


class EllipseItem(QGraphicsEllipseItem):
    """An ellipse that supports scaling with draggable points."""

    def __init__(self, x, y, width, height, view: ZoomableView):
        super().__init__(x, y, width, height)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)  # Enable selection
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)  # Enable selection
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.setPen(QPen(Qt.GlobalColor.white))  # Set border color
        self.setBrush(QBrush(Qt.GlobalColor.cyan))  # Set fill color

        self.view = view    # scene

        self.scale_points = []  # List of scale points (handles)
        self.scale_corners = []
        self.scale_edges = []

    def itemChange(self, change, value):
        """Override itemChange to track position changes."""
        print(f"New position: {self.pos().x()} {self.pos().y()}")
        return super().itemChange(change, value)



    def focusInEvent(self, event):
        super().focusInEvent(event)

        if self.view.scale_mode:
            self.view.hide_objs_scale_points()
            self.show_scale_points()

    def update_scale_contour(self):
        rect = self.rect()

        self.scale_corners = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomRight(),
            rect.bottomLeft(),
        ]
        self.scale_edges = [
            QPointF(rect.center().x(), rect.top()),  # Top-center (horizontal scaling)
            QPointF(rect.center().x(), rect.bottom()),  # Bottom-center (horizontal scaling)
            QPointF(rect.right(), rect.center().y()),  # Right-center (vertical scaling)
            QPointF(rect.left(), rect.center().y()),  # Left-center (vertical scaling)
        ]

    def show_scale_points(self):
        """Create and display scale points at the corners and edges of the object."""
        if not self.scale_points:
            self.update_scale_contour()

            for i, corner in enumerate(self.scale_corners):
                opposite_corner = self.scale_corners[(i + 2) % 4]  # Opposite corner is two indices away in a square
                point = ScalePoint(corner.x(), corner.y(), self)
                point.opposite_point = opposite_corner
                self.scene().addItem(point)
                self.scale_points.append(point)

            for i, edge in enumerate(self.scale_edges):
                opposite_edge_center = self.scale_edges[(i + 2) % len(self.scale_edges)]  # Opposite edge center
                direction = "horizontal" if i >= 2 else "vertical"
                point = ScalePoint(edge.x(), edge.y(), self, opposite_point=opposite_edge_center, direction=direction)
                self.scene().addItem(point)
                self.scale_points.append(point)

    def hide_scale_points(self):
        """Remove all scale points from the scene."""
        for point in self.scale_points:
            self.scene().removeItem(point)
        self.scale_points.clear()

    def update_scale_points(self):
        """Update the positions of the scale points based on the object's size."""
        self.update_scale_contour()

        for i, corner in enumerate(self.scale_corners):
            if i < len(self.scale_points):
                point = self.scale_points[i]
                point.setRect(corner.x() - 5, corner.y() - 5, 10, 10)

        for i, edge in enumerate(self.scale_edges):
            index = len(self.scale_corners) + i
            if index < len(self.scale_points):
                point = self.scale_points[index]
                point.setRect(edge.x() - 5, edge.y() - 5, 10, 10)


def main():
    app = QApplication(sys.argv)

    # Create a graphics scene
    scene = QGraphicsScene()
    scene.setSceneRect(-SCENE_SIZE / 2, -SCENE_SIZE / 2, SCENE_SIZE, SCENE_SIZE)  # Define coordinate bounds


    # Create a zoomable view and set the scene
    view = ZoomableView(scene)
    view.setWindowTitle("Scalable Items with Center Points")

    ellipse1 = EllipseItem(-100, -50, 200, 100, view)
    ellipse2 = EllipseItem(200, 200, 150, 75, view)
    scene.addItem(ellipse1)
    scene.addItem(ellipse2)

    view.resize(800, 600)
    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
