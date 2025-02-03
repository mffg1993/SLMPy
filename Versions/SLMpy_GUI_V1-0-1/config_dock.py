from PyQt5.QtWidgets import QLabel, QFormLayout, QDoubleSpinBox, QSpinBox, QDockWidget, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class ConfigDock:
    """
    Handles the configuration dock that dynamically generates widgets.
    """

    def __init__(self, parent, screen_index):
        # Initialize the configuration dock with parent and screen index
        self.parent = parent
        self.screen_index = screen_index
        self.parameter_controls = {}

        # Create the dock widget
        self.dock = QDockWidget(f"Screen {screen_index} Configuration", parent)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)  
        
        # Set up the main layout and form layout
        self.dock_widget = QWidget()
        self.main_layout = QVBoxLayout(self.dock_widget)  # ✅ Use QVBoxLayout instead of QFormLayout

        self.form_layout = QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        # Add the apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_parameters)
        self.main_layout.addWidget(self.apply_button)  # ✅ Ensure apply button is included in layout

        # Set the dock widget and add it to the parent
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
                widget.setSingleStep(0.01)

            widget.setValue(param["default"])
            self.form_layout.addRow(label, widget)  # ✅ Add to form layout
            self.parameter_controls[param["name"]] = widget

    def update_dock(self, category, widget_data):
        """
        Update the dock when a new content type is selected.
        """
        # Clear existing widgets
        for i in reversed(range(self.form_layout.count())):
            self.form_layout.itemAt(i).widget().setParent(None)

        # Create new widgets
        self.create_widgets(category, widget_data)
        self.dock.show()

    def apply_parameters(self):
        """
        Read parameters from dynamically created widgets and update the display.
        """
        screen_index = self.screen_index  # Ensure correct screen index

        if screen_index not in self.parent.parameters:
            print(f"[DEBUG] Initializing parameters for Screen {screen_index}")  # ✅ Debug print
            self.parent.parameters[screen_index] = {}

        content_type = self.parent.parameters[screen_index].get("type", None)
        if content_type is None:
            print(f"[DEBUG] No valid content type for Screen {screen_index}")  # ✅ Debug print
            return  # ✅ Exit if no content type is selected

        # ✅ Collect new parameter values
        parameters = {}
        for param_name, widget in self.parameter_controls.items():
            parameters[param_name] = widget.value()
            print(f"[DEBUG] Updated {param_name} = {parameters[param_name]} for Screen {screen_index}")

        # ✅ Save parameters before updating display
        param_key = content_type.lower().replace(" ", "_")
        self.parent.parameters[screen_index][param_key] = parameters
        print(f"[DEBUG] Stored new parameters for {content_type}: {parameters}")

        # ✅ Force refresh of display
        print(f"[DEBUG] Applying parameters and refreshing display for Screen {screen_index}")
        self.parent.update_display(screen_index)
