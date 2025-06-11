from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QGridLayout


class PropertiesPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for label, value, unit in [
            ("Refractive index", 1.65, ""),
            ("Absorption coefficient", 0.001, "m⁻¹"),
        ]:
            row = QVBoxLayout()
            column = QGridLayout()
            row.addWidget(QLabel(f"{label}:"))
            column.addWidget(QSlider(Qt.Orientation.Horizontal), 0, 0)
            column.addWidget(QLabel(f"{value} {unit}"), 0, 1)
            column.setColumnStretch(0, 4)  # 80%
            column.setColumnStretch(1, 1)  # 20%
            row.addLayout(column)
            layout.addLayout(row)
        self.setLayout(layout)

    def handle_panel_update(self, item):
        """
        Update the properties panel based on the selected item.
        :param item: The selected item from the scene.
        """
        if not hasattr(item, "source_point"): # Check if the item is not a laser
            print(item)
            self.show()
        else:
            self.hide()