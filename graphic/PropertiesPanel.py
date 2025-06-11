from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QGridLayout
from render.Mirror import Mirror
from render.Ray import Ray


class PropertiesPanel(QWidget):
    class MaterialPropertiesData:
        def __init__(self):
            self.selected_item = None

            self.refractive_index = 0
            self.refraction_label = QLabel(str(self.refractive_index))
            self.refraction_slider = self.generate_refraction_slider()[0]

            self.absorption_coefficient = 0
            self.absorption_label = QLabel(str(self.absorption_coefficient))
            self.absorption_slider = self.generate_absorption_slider()[0]

        def select_item(self, item):
            """
            Select an item and update the properties panel.
            :param item: The item to select.
            """
            if item is None:
                return
            self.selected_item = item
            self.refraction_slider.setValue(int(item.controller.material.refractive_index * 10))
            self.refraction_label.setText(f"{item.controller.material.refractive_index}")
            self.absorption_slider.setValue(int(item.controller.material.absorption_coefficient * 1000))

        def handle_refraction_change(self, value):
            if self.selected_item is None:
                return
            print("Refraction changed to:", value / 10)
            self.selected_item.controller.material.refractive_index = value / 10
            self.refraction_label.setText(f"{value / 10:.1f}")

        def handle_absorption_change(self, value):
            if self.selected_item is None:
                return
            print("Absorption changed to:", value / 1000)
            self.selected_item.controller.material.absorption_coefficient = value / 1000
            self.absorption_label.setText(f"{value / 1000:.3f} m⁻¹")

        def generate_refraction_slider(self):
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 1000)
            slider.setSingleStep(1)
            slider.valueChanged.connect(self.handle_refraction_change)
            self.refraction_slider = slider
            return [slider, self.refraction_label]

        def generate_absorption_slider(self):
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 20000)
            slider.setSingleStep(1)
            slider.valueChanged.connect(self.handle_absorption_change)
            self.absorption_slider = slider
            return [slider, self.absorption_label]

    def __init__(self):
        super().__init__()
        self.selected_item = None
        self.data = self.MaterialPropertiesData()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for label, slider, value_label in [
            ("Refractive index", *self.data.generate_refraction_slider()),
            ("Absorption coefficient", *self.data.generate_absorption_slider()),
        ]:
            row = QVBoxLayout()
            column = QGridLayout()
            row.addWidget(QLabel(f"{label}:"))
            column.addWidget(slider, 0, 0)
            column.addWidget(value_label, 0, 1)
            column.setColumnStretch(0, 4)  # 80%
            column.setColumnStretch(1, 1)  # 20%
            row.addLayout(column)
            layout.addLayout(row)
        self.setLayout(layout)
        self.hide()

    def handle_panel_update(self, item: Mirror):
        """
        Update the properties panel based on the selected item.
        :param item: The selected item from the scene.
        """
        if not hasattr(item, "source_point") and not isinstance(item, Ray):  # Check if the item is not a laser
            print(item)
            self.data.select_item(item)
            self.show()
        else:
            self.hide()
