"""
ConfigDock - Configuration Panel for Multi-Screen Display

This module defines the `ConfigDock` class, which provides a user interface for configuring
parameters related to different display content types. The dock dynamically generates widgets
based on the selected content type, allowing users to modify and apply parameters.

Author: Manuel Ferrer (@mferrerg)
"""

from PyQt5.QtWidgets import QLabel, QFormLayout, QDoubleSpinBox, QSpinBox, QComboBox, QDockWidget, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class ConfigDock:
    """
    Handles the configuration dock that dynamically generates widgets for configuring display parameters.
    
    This class creates a dockable UI component that allows users to modify and apply parameters
    for different content types displayed on a multi-screen setup.
    """

    def __init__(self, parent, screen_index):
        """
        Initializes the configuration dock.

        Parameters:
        parent : QWidget
            The main application window to which this dock belongs.
        screen_index : int
            The index of the screen this configuration dock is associated with.
        """
        self.parent = parent
        self.screen_index = screen_index
        self.parameter_controls = {}

        # Create the dock widget
        self.dock = QDockWidget(f"Screen {screen_index} Configuration", parent)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)  
        
        # Set up the main layout and form layout
        self.dock_widget = QWidget()
        self.main_layout = QVBoxLayout(self.dock_widget)
        self.form_layout = QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        # Add the apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_parameters)
        self.main_layout.addWidget(self.apply_button)

        # Set the dock widget and add it to the parent
        self.dock.setWidget(self.dock_widget)
        parent.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.hide()

    def create_widgets(self, category, widget_data):
        """
        Dynamically creates UI widgets based on the specified category.

        Parameters:
        category : str
            The type of content being configured.
        widget_data : list of dict
            A list of dictionaries containing widget specifications (name, type, range, default values, etc.).
        """
        self.parameter_controls = {}

        for param in widget_data:
            label = QLabel(f"{param['name']}:")
            if param["type"] == "spinbox":
                widget = QSpinBox()
                widget.setRange(*param["range"])
                widget.setValue(param["default"])
            elif param["type"] == "doublespinbox":
                widget = QDoubleSpinBox()
                widget.setRange(*param["range"])
                widget.setSingleStep(0.01)
                widget.setValue(param["default"])
            elif param["type"] == "combobox":
                widget = QComboBox()
                widget.addItems(param["options"])
                widget.setCurrentText(param["default"])

            self.form_layout.addRow(label, widget)
            self.parameter_controls[param["name"]] = widget

    def update_dock(self, category, widget_data):
        """
        Updates the dock when a new content type is selected, clearing existing widgets and creating new ones.

        Parameters:
        category : str
            The type of content being configured.
        widget_data : list of dict
            A list of dictionaries containing widget specifications.
        """
        # Clear existing widgets
        for i in reversed(range(self.form_layout.count())):
            self.form_layout.itemAt(i).widget().setParent(None)

        # Create new widgets
        self.create_widgets(category, widget_data)
        self.dock.show()

    def apply_parameters(self):
        """
        Reads parameters from dynamically created widgets and updates the display accordingly.
        """
        screen_index = self.screen_index

        if screen_index not in self.parent.parameters:
            self.parent.parameters[screen_index] = {}

        content_type = self.parent.parameters[screen_index].get("type", None)
        if content_type is None:
            return  # Exit if no content type is selected

        # Collect new parameter values
        parameters = {}
        for param_name, widget in self.parameter_controls.items():
            if isinstance(widget, QComboBox):
                parameters[param_name] = widget.currentText()
            else:
                parameters[param_name] = widget.value()

        # Save parameters before updating display
        param_key = content_type.lower().replace(" ", "_")
        self.parent.parameters[screen_index][param_key] = parameters

        # Refresh display with updated parameters
        self.parent.update_display(screen_index)
