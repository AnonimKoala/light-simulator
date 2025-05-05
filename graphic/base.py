import math
from typing import Any

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QBrush, QPen, QFont, QWheelEvent, QMouseEvent, QKeyEvent, QFocusEvent
from PyQt6.QtWidgets import QGraphicsView, QGraphicsItem, QGraphicsEllipseItem, QGraphicsSimpleTextItem, \
    QGraphicsSceneMouseEvent, QGraphicsScene

from graphic.config import FONT_SIZE
from tools import convert_qt_angle2cartesian


class ScalePoint(QGraphicsEllipseItem):
    """A small draggable point used for scaling."""

    def __init__(self, x: float, y: float, parent_item: 'SceneItem', opposite_point: QPointF = None,
                 direction: str = None):
        """
        Initialize a ScalePoint.

        :param x: float - X-coordinate of the point.
        :param y: float - Y-coordinate of the point.
        :param parent_item: SceneItem - The parent item that this point will scale.
        :param opposite_point: QPointF - The opposite point used for scaling.
        :param direction: str - The direction of scaling ('horizontal' or 'vertical').
        """
        super().__init__(x - 5, y - 5, 10, 10)  # Create a small circle
        self.setBrush(QBrush(Qt.GlobalColor.red))  # Red color for scale points
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)  # Enable dragging
        self.parent_item = parent_item  # Reference to the parent item (scalable object)
        self.opposite_point = opposite_point  # The fixed point during scaling
        self.direction = direction  # Direction for scaling (horizontal/vertical)
        self.setZValue(2)  # Ensure scale points are always on top

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        """
        Handle dragging of the scale point to resize the parent item.

        :param event: QGraphicsSceneMouseEvent - The mouse move event.
        """
        view = self.parent_item.scene().views()[0]
        if isinstance(view, ZoomableView) and not view.scale_mode:
            return

        current_pos = self.mapToParent(event.pos())
        rect = self.parent_item.rect()

        if self.direction is None:  # Corner scaling
            if self.opposite_point is not None:
                dx = current_pos.x() - self.opposite_point.x()
                dy = current_pos.y() - self.opposite_point.y()

                # Maintain aspect ratio
                if abs(dx) > abs(dy):
                    new_width = abs(dx)
                    new_height = new_width * (rect.height() / rect.width())
                else:
                    new_height = abs(dy)
                    new_width = new_height * (rect.width() / rect.height())

                if current_pos.x() < self.opposite_point.x():
                    new_x = self.opposite_point.x() - new_width
                else:
                    new_x = self.opposite_point.x()

                if current_pos.y() < self.opposite_point.y():
                    new_y = self.opposite_point.y() - new_height
                else:
                    new_y = self.opposite_point.y()

                self.parent_item.setRect(new_x, new_y, new_width, new_height)
        elif self.direction == "horizontal":
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

    def __init__(self, scene: QGraphicsScene):
        """
        Initialize the ZoomableView.

        :param scene: QGraphicsScene - The QGraphicsScene to be displayed in the view.
        """
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

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle key press events for toggling scalability, moving, and rotation modes.

        :param event: QKeyEvent - The key press event.
        """
        if event.key() == Qt.Key.Key_S:  # Press 'S' to toggle scale mode for selected items
            self.toggle_items_scaling()

        elif event.key() == Qt.Key.Key_M:
            self.toggle_items_moving()

        elif event.key() == Qt.Key.Key_R:  # Toggle rotation mode when 'R' is pressed
            self.toggle_items_rotation()

            print("Rotation mode:", "ON" if self.rotation_mode else "OFF")

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle mouse press events for initiating rotation.

        :param event: QMouseEvent - The mouse press event.
        """
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

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Handle mouse move events for rotating the selected item.

        :param event: QMouseEvent - The mouse move event.
        """
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

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Handle mouse release events to finalize rotation.

        :param event: QMouseEvent - The mouse release event.
        """
        if self.rotation_mode and event.button() == Qt.MouseButton.LeftButton:
            if self.selected_item:
                print("Rotation ended")
                final_angle = self.selected_item.rotation()
                print(f"Final Angle: {final_angle:.2f}°")
                self.selected_item.update_hint_text(final_angle)
                self.selected_item.hide_hint()  # Hide the rotation hint after releasing the mouse button
            self.selected_item = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """
        Handle mouse wheel events for zooming in and out.

        :param event: QWheelEvent - The mouse wheel event.
        """
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
            self.scale_factor *= zoom_factor
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)
            self.scale_factor /= zoom_factor

        self.update_hint_font()

    def update_hint_font(self):
        """Update the font size of the rotation hint based on the current scale factor."""
        for item in self.scene().items():
            if isinstance(item, SceneItem):
                item.font.setPointSize(int(FONT_SIZE / self.scale_factor))
                item.rotation_hint.setFont(item.font)
                item.update_hint_position()

    def enable_items_moving(self):
        """Enable moving mode for items."""
        self.disable_items_rotation()
        self.moving_mode = True
        self.update_items_move_state()

    def enable_items_scaling(self):
        """Enable scaling mode for items."""
        self.disable_items_rotation()
        self.disable_items_scaling()
        self.scale_mode = True
        selected_item = self.scene().selectedItems()[0] if self.scene().selectedItems() else None
        if isinstance(selected_item, SceneItem):
            selected_item.show_scale_points()

    def enable_items_rotation(self):
        """Enable rotation mode for items."""
        self.disable_items_moving()
        self.disable_items_scaling()
        self.rotation_mode = True

    def disable_items_moving(self):
        """Disable moving mode for items."""
        self.moving_mode = False
        self.update_items_move_state()

    def disable_items_scaling(self):
        """Disable scaling mode for items."""
        self.scale_mode = False
        for item in self.scene().items():
            if isinstance(item, SceneItem):
                item.hide_scale_points()

    def disable_items_rotation(self):
        """Disable rotation mode for items."""
        self.rotation_mode = False

        for item in self.scene().items():
            if isinstance(item, SceneItem):
                item.hide_hint()

    def update_items_move_state(self):
        """Update the movable state of items based on the current moving mode."""
        for item in self.items():
            if isinstance(item, SceneItem):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, self.moving_mode)

    def toggle_items_moving(self):
        """Toggle the moving mode for items."""
        self.moving_mode = not self.moving_mode
        if self.moving_mode:
            self.enable_items_moving()
        else:
            self.disable_items_moving()

    def toggle_items_scaling(self):
        """Toggle the scaling mode for items."""
        self.scale_mode = not self.scale_mode

        if self.scale_mode:
            self.enable_items_scaling()
        else:
            self.disable_items_scaling()

    def toggle_items_rotation(self):
        """Toggle the rotation mode for items."""
        self.rotation_mode = not self.rotation_mode

        if self.rotation_mode:
            self.enable_items_rotation()
        else:
            self.disable_items_rotation()


class SceneItem(QGraphicsItem):
    """An ellipse that supports scaling with draggable points."""

    def __init__(self, x: float, y: float, width: float, height: float, view: 'ZoomableView'):
        """
        Initialize the SceneItem.

        :param x: float - X-coordinate of the item.
        :param y: float - Y-coordinate of the item.
        :param width: float - Width of the item.
        :param height: float - Height of the item.
        :param view: ZoomableView - The ZoomableView that contains this item.
        """
        super().__init__()
        self.setPos(x, y)  # Set position separately
        self.setRect(0, 0, width, height)

        self.width = width
        self.height = height

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)  # Enable selection
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)  # Enable focus
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

        self.view = view  # Reference to the ZoomableView

        self.scale_points = []  # List of scale points (handles)
        self.scale_corners = []
        self.scale_edges = []

    def setRect(self, x: float, y: float, width: float, height: float):
        """
        Set the rectangle with the given position and size.

        :param x: float - X-coordinate of the rectangle.
        :param y: float - Y-coordinate of the rectangle.
        :param width: float - Width of the rectangle.
        :param height: float - Height of the rectangle.
        """
        self.setPos(x, y)
        self.width = width
        self.height = height
        self.prepareGeometryChange()

    def rect(self) -> QRectF:
        """
        Get the rectangle representing the item's bounds.

        :return: QRectF object representing the item's bounds.
        """
        return QRectF(0, 0, self.width, self.height)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """
        Override itemChange to track position changes.

        :param change: QGraphicsItem.GraphicsItemChange - The type of change.
        :param value: Any - The new value.
        :return: Any - The result of the base class implementation.
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            print(f"New position: {self.pos().x()} {self.pos().y()}")
        return super().itemChange(change, value)

    def focusInEvent(self, event: QFocusEvent):
        """
        Handle focus in events to enable scaling mode.

        :param event: QFocusEvent - The focus in event.
        """
        if self.isSelected() and self.view.scale_mode and not self.scale_points:
            print("Focused item:", self)
            self.view.enable_items_scaling()
        super().focusInEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """
        Handle mouse press events to select the item and enable scaling mode.

        :param event: QGraphicsSceneMouseEvent - The mouse press event.
        """
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

    def update_hint_text(self, angle: float | int):
        """
        Update the text of the rotation hint.

        :param angle: float - The new rotation angle.
        """
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
        """Update the positions of the scale points based on the object's size."""
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
        """Set the rotation origin to the center of the bounding rectangle."""
        self.setTransformOriginPoint(self.boundingRect().center())  # Set rotation origin
