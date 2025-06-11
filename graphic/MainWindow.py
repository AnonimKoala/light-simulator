from PyQt6.QtWidgets import QWidget, QHBoxLayout
from graphic.PropertiesPanel import PropertiesPanel


class MainWindow(QWidget):
    def __init__(self, view):
        super().__init__()
        self.setWindowTitle("Light Simulator")
        self.resize(1000, 600)
        layout = QHBoxLayout(self)
        layout.addWidget(view)
        view.setRenderHint(
            view.renderHints() | view.renderHints().Antialiasing)  # Enable antialiasing for smoother graphics
        panel = PropertiesPanel()
        view.set_props_panel(panel)
        layout.addWidget(panel)
        panel.setFixedWidth(250)
        self.setLayout(layout)
