import math
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QKeyEvent, QMouseEvent, QWheelEvent
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from graphic.base import SceneItem
from graphic.config import FONT_SIZE


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
        self.props_panel = None

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

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        print(self.mapToScene(event.pos()))
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle mouse press events for initiating rotation.

        :param event: QMouseEvent - The mouse press event.
        """
        item = self.itemAt(event.pos())
        if self.props_panel and item:
            self.props_panel.handle_panel_update(item)
        if self.rotation_mode and event.button() == Qt.MouseButton.LeftButton:
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
            angle = int(round(math.degrees(math.atan2(current_pos.y() - center_pos.y(),
                                                      current_pos.x() - center_pos.x()))))
            initial_angle = int(round(math.degrees(math.atan2(self.origin_pos.y() - center_pos.y(),
                                                              self.origin_pos.x() - center_pos.x()))))

            # Calculate rotation difference
            rotation_diff = int(angle - initial_angle)

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
            self.selected_item.update_hint_text(rotation_angle)
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
        print("Scaling is not implemented!")
        self.scale_mode = False
        # self.scale_mode = not self.scale_mode
        # if self.scale_mode:
        #     self.enable_items_scaling()
        # else:
        #     self.disable_items_scaling()

    def toggle_items_rotation(self):
        """Toggle the rotation mode for items."""
        self.rotation_mode = not self.rotation_mode

        if self.rotation_mode:
            self.enable_items_rotation()
        else:
            self.disable_items_rotation()

    def set_props_panel(self, panel):
        """
        Set the properties panel for the view.

        :param panel: The properties panel to be set.
        """
        self.props_panel = panel
