from PyQt5.QtWidgets import QLabel, QFormLayout, QDoubleSpinBox, QSpinBox, QDockWidget, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class ConfigDock:
    """
    Handles the configuration dock that dynamically generates widgets.
    """

    def __init__(self, parent, screen_index):
        self.parent = parent
        self.screen_index = screen_index
        self.parameter_controls = {}

        self.dock = QDockWidget(f"Screen {screen_index} Configuration", parent)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)  
        
        self.dock_widget = QWidget()
        self.main_layout = QVBoxLayout(self.dock_widget)  # ✅ Use QVBoxLayout instead of QFormLayout

        self.form_layout = QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(lambda: self.apply_parameters())
        self.main_layout.addWidget(self.apply_button)  # ✅ Ensure apply button is included in layout

        self.dock.setWidget(self.dock_widget)
        parent.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.hide()

    def create_widgets(self, category, widget_data):
        """
        Create widgets dynamically based on category.
        """
        self.parameter_controls = {}

        for param in widget_data:
            label = QLabel(f"{param['name']}:")
            if param["type"] == "spinbox":
                widget = QSpinBox()
                widget.setRange(*param["range"])
            elif param["type"] == "doublespinbox":
                widget = QDoubleSpinBox()
                widget.setRange(*param["range"])
                widget.setSingleStep(0.05)

            widget.setValue(param["default"])
            self.form_layout.addRow(label, widget)  # ✅ Add to form layout
            self.parameter_controls[param["name"]] = widget

    def update_dock(self, category, widget_data):
        """
        Update the dock when a new content type is selected.
        """
        for i in reversed(range(self.form_layout.count())):
            self.form_layout.itemAt(i).widget().setParent(None)

        self.create_widgets(category, widget_data)
        self.dock.show()

    def apply_parameters(self):
        """
        Save parameters from UI.
        """
        parameters = {name: widget.value() for name, widget in self.parameter_controls.items()}
        self.parent.parameters[self.screen_index] = parameters
        self.parent.update_display(self.screen_index)
