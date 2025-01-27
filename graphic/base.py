import math

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QBrush, QPen, QFont
from PyQt6.QtWidgets import QGraphicsView, QGraphicsItem, QGraphicsEllipseItem, QGraphicsSimpleTextItem

from graphic.config import FONT_SIZE
from tools import convert_qt_angle2cartesian


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

        current_pos = self.mapToParent(event.pos())
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

        self.scale_factor = 1.0

        self.scale_mode = False
        self.moving_mode = False
        self.rotation_mode = False

        self.selected_item = None  # Track the currently selected item

        # For rotation
        self.start_rotation = None
        self.origin_pos = None

    def keyPressEvent(self, event):
        """Handle key press events for toggling scalability."""
        if event.key() == Qt.Key.Key_S:  # Press 'S' to toggle scale mode for selected items
            self.toggle_items_scaling()

        elif event.key() == Qt.Key.Key_M:
            self.toggle_items_moving()

        elif event.key() == Qt.Key.Key_R:  # Toggle rotation mode when 'R' is pressed
            self.toggle_items_rotation()

            print("Rotation mode:", "ON" if self.rotation_mode else "OFF")

    def mousePressEvent(self, event):
        if self.rotation_mode and event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item and isinstance(item, SceneItem):
                item.update_transform_origin()
                item.update_hint_position()

                self.selected_item = item
                self.origin_pos = self.mapToScene(event.pos())

                # Store the current rotation angle
                self.start_rotation = item.rotation()

                self.selected_item.show_hint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.rotation_mode and self.selected_item:
            current_pos = self.mapToScene(event.pos())
            center_pos = self.selected_item.sceneBoundingRect().center()

            # Calculate instantaneous angle
            angle = math.degrees(math.atan2(current_pos.y() - center_pos.y(),
                                            current_pos.x() - center_pos.x()))
            initial_angle = math.degrees(math.atan2(self.origin_pos.y() - center_pos.y(),
                                                    self.origin_pos.x() - center_pos.x()))

            # Calculate rotation difference
            rotation_diff = angle - initial_angle

            # Determine rotation direction
            if rotation_diff > 0:
                # Rotating left (0 to 360)
                rotation_angle = self.start_rotation + rotation_diff
                rotation_angle = min(rotation_angle, 360)
            else:
                # Rotating right (0 to -360)
                rotation_angle = self.start_rotation + rotation_diff
                rotation_angle = max(rotation_angle, -360)

            if abs(rotation_angle) == 360:
                rotation_angle = 0

            self.selected_item.setRotation(rotation_angle)
            self.selected_item.update_hint_text(convert_qt_angle2cartesian(rotation_angle))
            print(
                f"Current Angle: {convert_qt_angle2cartesian(rotation_angle):.2f}\t"
                f"Start: {self.start_rotation} Diff: {rotation_diff}°"
            )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.rotation_mode and event.button() == Qt.MouseButton.LeftButton:
            if self.selected_item:
                print("Rotation ended")
                final_angle = self.selected_item.rotation()
                print(f"Final Angle: {final_angle:.2f}°")
                self.selected_item.update_hint_text(final_angle)
                self.selected_item.hide_hint()  # Hide the rotation hint after releasing the mouse button
            self.selected_item = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
            self.scale_factor *= zoom_factor
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)
            self.scale_factor /= zoom_factor

        self.update_hint_font()

    def update_hint_font(self):
        for item in self.scene().items():
            if isinstance(item, SceneItem):
                item.font.setPointSize(int(FONT_SIZE / self.scale_factor))
                item.rotation_hint.setFont(item.font)
                item.update_hint_position()

    def enable_items_moving(self):
        self.disable_items_rotation()
        self.moving_mode = True
        self.update_items_move_state()

    def enable_items_scaling(self):
        self.disable_items_rotation()
        self.disable_items_scaling()
        self.scale_mode = True
        selected_item = self.scene().selectedItems()[0] if self.scene().selectedItems() else None
        if isinstance(selected_item, SceneItem):
            selected_item.show_scale_points()

    def enable_items_rotation(self):
        self.disable_items_moving()
        self.disable_items_scaling()
        self.rotation_mode = True

    def disable_items_moving(self):
        self.moving_mode = False
        self.update_items_move_state()

    def disable_items_scaling(self):
        self.scale_mode = False
        for item in self.scene().items():
            if isinstance(item, SceneItem):
                item.hide_scale_points()

    def disable_items_rotation(self):
        self.rotation_mode = False

        for item in self.scene().items():
            if isinstance(item, SceneItem):
                item.hide_hint()

    def update_items_move_state(self):
        for item in self.items():
            if isinstance(item, SceneItem):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, self.moving_mode)

    def toggle_items_moving(self):
        self.moving_mode = not self.moving_mode
        if self.moving_mode:
            self.enable_items_moving()
        else:
            self.disable_items_moving()

    def toggle_items_scaling(self):
        self.scale_mode = not self.scale_mode

        if self.scale_mode:
            self.enable_items_scaling()
        else:
            self.disable_items_scaling()

    def toggle_items_rotation(self):
        self.rotation_mode = not self.rotation_mode

        if self.rotation_mode:
            self.enable_items_rotation()
        else:
            self.disable_items_rotation()


class SceneItem(QGraphicsItem):
    """An ellipse that supports scaling with draggable points."""

    def __init__(self, x, y, width, height, view: ZoomableView):
        super().__init__()
        self.setPos(x, y)  # Set position separately
        self.setRect(0, 0, width, height)

        self.width = width
        self.height = height

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)  # Enable selection
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)  # Enable selection
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        # Create a text item for the rotation hint
        self.rotation_hint = QGraphicsSimpleTextItem("0°")
        self.rotation_hint.setZValue(1)  # Ensure it's on top of other items
        self.rotation_hint.setBrush(QBrush(Qt.GlobalColor.white))  # Set text color to white
        self.font = QFont("Arial", FONT_SIZE)  # Default font size
        self.rotation_hint.setFont(self.font)

        view.scene().addItem(self.rotation_hint)  # Add hint directly to the scene
        self.rotation_hint.setVisible(False)  # Initially hide the hint
        self.update_hint_position()
        self.update_transform_origin()

        self.view = view  # scene

        self.scale_points = []  # List of scale points (handles)
        self.scale_corners = []
        self.scale_edges = []

    def setRect(self, x, y, width, height):
        """Set the rectangle with the given position and size."""
        self.setPos(x, y)
        self.width = width
        self.height = height
        self.prepareGeometryChange()

    def rect(self):
        return QRectF(0, 0, self.width, self.height)

    def itemChange(self, change, value):
        """Override itemChange to track position changes."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            print(f"New position: {self.pos().x()} {self.pos().y()}")
        return super().itemChange(change, value)

    def focusInEvent(self, event):
        if self.isSelected() and self.view.scale_mode and not self.scale_points:
            print("Focused item:", self)
            self.view.enable_items_scaling()
        super().focusInEvent(event)

    def mousePressEvent(self, event):
        if not self.isSelected():
            self.scene().clearSelection()
            self.setSelected(True)
            if self.view.scale_mode:
                print("Selected item:", self)
                self.view.enable_items_scaling()

        super().mousePressEvent(event)

    def show_hint(self):
        """Show the rotation hint."""
        self.rotation_hint.setVisible(True)

    def hide_hint(self):
        """Hide the rotation hint."""
        self.rotation_hint.setVisible(False)

    def update_hint_position(self):
        """Update the position of the rotation hint."""
        center = self.sceneBoundingRect().center()  # Get center in scene coordinates
        self.rotation_hint.setPos(center.x() - self.rotation_hint.boundingRect().width() / 2,
                                  center.y() - self.rotation_hint.boundingRect().height() / 2)

    def update_hint_text(self, angle):
        """Update the text of the rotation hint."""
        self.rotation_hint.setText(f"{int(angle)}°")

    def show_scale_points(self):
        """Create and display scale points at the corners and edges of the object."""
        if not self.scale_points:
            self.update_scale_contour()

            for i, corner in enumerate(self.scale_corners):
                opposite_corner = self.scale_corners[(i + 2) % 4]
                point = ScalePoint(corner.x(), corner.y(), self)
                point.opposite_point = opposite_corner
                point.setParentItem(self)  # Set as child item
                self.scale_points.append(point)

            for i, edge in enumerate(self.scale_edges):
                opposite_edge_center = self.scale_edges[(i + 2) % len(self.scale_edges)]
                direction = "horizontal" if i >= 2 else "vertical"
                point = ScalePoint(edge.x(), edge.y(), self, opposite_point=opposite_edge_center, direction=direction)
                point.setParentItem(self)  # Set as child item
                self.scale_points.append(point)

    def hide_scale_points(self):
        """Remove all scale points from the scene."""
        if not self.scale_points:
            return
        for point in self.scale_points:
            point.setParentItem(None)  # Remove parent before deleting
            self.scene().removeItem(point)
        self.scale_points.clear()

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

    def update_transform_origin(self):
        self.setTransformOriginPoint(self.boundingRect().center())  # Set rotation origin
