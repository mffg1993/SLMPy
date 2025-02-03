"""
MultiScreenController - GUI for Managing Multi-Screen Displays

This module defines the `MultiScreenController` class, which provides a user interface for configuring,
updating, and displaying content on multiple screens. It supports various content types, including
holograms, noise patterns, gradients, and zeros, with the ability to apply colormaps dynamically.

Author: Manuel Ferrer (@mferrerg)
"""

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox, QHBoxLayout, QPushButton, QApplication
)
from PyQt5.QtCore import Qt
from functools import partial
import numpy as np
import os
from display import ArrayDisplay
from holograms import HoloLG, HoloHG
from config_dock import ConfigDock
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt


def load_colormaps():
    """Loads colormaps from the Cmaps directory and returns a dictionary."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Ensures saving in the same folder as the script
    subfolder_path = os.path.join(script_dir, "Cmaps")
    
    if not os.path.exists(subfolder_path):
        return {"gray": plt.get_cmap("gray")}  # Default to gray if folder is missing

    cmap_files = [f for f in os.listdir(subfolder_path) if f.endswith(".cmap")]
    Cmap_Dict = {}

    for cmap_file in cmap_files:
        cmap_name = os.path.splitext(cmap_file)[0]
        cmap_path = os.path.join(subfolder_path, cmap_file)
        try:
            cmap_data = np.loadtxt(cmap_path)
            Cmap_Dict[cmap_name] = LinearSegmentedColormap.from_list(cmap_name, cmap_data)
        except Exception:
            pass  # Ignore colormap loading errors

    Cmap_Dict["gray"] = plt.get_cmap("gray")  # Ensure the default gray colormap is available
    return Cmap_Dict

# Load colormaps at startup
Cmap_Dict = load_colormaps()
cmap_list = list(Cmap_Dict.keys())


class MultiScreenController(QMainWindow):
    """
    GUI for managing multiple screens and displaying different types of content.
    
    Allows users to configure display content for each screen, set parameters, and apply colormaps.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Screen Display Controller")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.displays = {}  # Holds active display windows
        self.screens = QApplication.screens()  # Retrieve available screens
        self.parameters = {i: {"type": None} for i in range(len(self.screens))}  # Store screen parameters
        self.config_docks = {}  # Store configuration panels

        self.widgets = {  # Configuration options for each content type
            "LG Hologram": [
                {"name": "l", "type": "spinbox", "range": (-10, 10), "default": 0},
                {"name": "p", "type": "spinbox", "range": (0, 10), "default": 0},
                {"name": "w0", "type": "doublespinbox", "range": (0.1, 5.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "LA", "type": "doublespinbox", "range": (0.1, 1.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "x", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01},
                {"name": "y", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01},
                {"name": "Cmap", "type": "combobox", "options": cmap_list, "default": "gray"}
            ],
            "HG Hologram": [...],
            "Random Noise": [...],
            "Gradient": [...],
            "None": [],
            "Zeros": [],
        }

        self.init_ui()
        self.init_config_docks()

    def init_ui(self):
        """Initializes the main UI components."""
        layout = QVBoxLayout(self.central_widget)
        instructions = QLabel("Select content for each screen and configure options.")
        layout.addWidget(instructions)

        self.screen_controls = []
        for idx, screen in enumerate(self.screens):
            screen_layout = QHBoxLayout()
            label = QLabel(f"Screen {idx}:")
            combobox = QComboBox()
            combobox.addItems(self.widgets.keys())
            combobox.setCurrentText("None")
            combobox.currentIndexChanged.connect(partial(self.update_content, idx, combobox))
            screen_layout.addWidget(label)
            screen_layout.addWidget(combobox)
            self.screen_controls.append(combobox)
            layout.addLayout(screen_layout)

        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.quit_application)
        layout.addWidget(quit_button)

    def update_display(self, screen_index):
        """Updates the display content for the specified screen."""
        if screen_index not in self.parameters:
            return
        content_type = self.parameters[screen_index].get("type", None)
        if content_type is None:
            return

        resolution = (self.screens[screen_index].geometry().width(), self.screens[screen_index].geometry().height())
        selected_cmap = "gray"
        array = None

        if content_type == "LG Hologram":
            params = self.parameters[screen_index].get("lg_hologram", {})
            pos = (-params.get("x", 0), -params.get("y", 0))
            array = HoloLG(params.get("l", 0), params.get("p", 0), params.get("w0", 0.2),
                           LA=params.get("LA", 0.2) / 100, SLM_Pix=resolution, position=pos)
            selected_cmap = params.get("Cmap", "gray")

        if array is not None:
            self.show_screen(screen_index, array, selected_cmap)
