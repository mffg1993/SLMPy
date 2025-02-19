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
        #
        return {"gray": plt.get_cmap("gray")}  # Default to gray if folder is missing

    cmap_files = [f for f in os.listdir(subfolder_path) if f.endswith(".cmap")]
    Cmap_Dict = {}

    for cmap_file in cmap_files:
        cmap_name = os.path.splitext(cmap_file)[0]
        cmap_path = os.path.join(subfolder_path, cmap_file)
        try:
            cmap_data = np.loadtxt(cmap_path)
            Cmap_Dict[cmap_name] = LinearSegmentedColormap.from_list(cmap_name, cmap_data)
        except Exception as e:
            print(f"[ERROR] Failed to load colormap {cmap_name}: {e}")


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

        # Widgets configuration for different content types
        self.widgets = {
            "LG Hologram": [
                {"name": "l", "type": "spinbox", "range": (-10, 10), "default": 0},
                {"name": "p", "type": "spinbox", "range": (0, 10), "default": 0},
                {"name": "w0", "type": "doublespinbox", "range": (0.1, 5.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "LA", "type": "doublespinbox", "range": (0.1, 1.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "x", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01},
                {"name": "y", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01},
                {"name": "Cmap", "type": "combobox", "options":cmap_list, "default": "gray"}
            ],
            "HG Hologram": [
                {"name": "l", "type": "spinbox", "range": (-10, 10), "default": 0},
                {"name": "p", "type": "spinbox", "range": (0, 10), "default": 0},
                {"name": "w0", "type": "doublespinbox", "range": (0.1, 5.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "LA", "type": "doublespinbox", "range": (0.1, 1.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "x", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01},
                {"name": "y", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01},
                {"name": "Cmap", "type": "combobox", "options": cmap_list, "default": "gray"}
            ],
            "Random Noise": [
                {"name": "mean", "type": "doublespinbox", "range": (0.0, 1.0), "default": 0.5},
                {"name": "std", "type": "doublespinbox", "range": (0.0, 1.0), "default": 0.1}
            ],
            "Gradient": [
                {"name": "direction", "type": "combobox", "options": ["horizontal", "vertical"], "default": "horizontal"},
                {"name":"scale","type":"doublespinbox","range":(0.1,1.0),"default":1.0,"SingleStep":0.01}
            
            ],
            "None":[

            ],
            "Zeros": [
            ],
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

    def init_config_docks(self):
        # Initialize configuration docks for each screen
        for idx in range(len(self.screens)):
            self.config_docks[idx] = ConfigDock(self, idx)

    def update_content(self, screen_index, combobox):
        # Update the content type for the selected screen
        content_type = combobox.currentText()
        if screen_index not in self.parameters:
            self.parameters[screen_index] = {"type": None}
        self.parameters[screen_index]["type"] = content_type

        # Update the configuration dock based on the selected content type
        if content_type in self.widgets:
            self.config_docks[screen_index].update_dock(content_type, self.widgets[content_type])
        else:
            self.config_docks[screen_index].dock.hide()

        # Update the display for the selected screen
        self.update_display(screen_index)

        # Get the resolution of the selected screen
        #step1 = self.screens[screen_index]
        #resolution = (step1.geometry().width(), step1.geometry().height())

    def update_display(self, screen_index): 
        """
        Update the display content for the specified screen.
        """
        if screen_index not in self.parameters:
            self.parameters[screen_index] = {"type": None}

        content_type = self.parameters[screen_index].get("type", None)

        if content_type is None:
            return  # Exit if no content type is selected

        step1 = self.screens[screen_index]
        resolution = (step1.geometry().width(), step1.geometry().height())

        selected_cmap = "gray"  # ✅ Default colormap
        array = None  # ✅ Ensure `array` is defined

        if content_type == "LG Hologram":
            params = self.parameters[screen_index].get("lg_hologram", {})
            pos = (-params.get("x", 0), -params.get("y", 0))
            array = HoloLG(
                params.get("l", 0), params.get("p", 0), params.get("w0", 0.2),
                LA=params.get("LA", 0.2) / 100, SLM_Pix=resolution, position=pos
            )
            selected_cmap = params.get("Cmap", "gray")

        elif content_type == "HG Hologram":
            params = self.parameters[screen_index].get("hg_hologram", {})
            pos = (-params.get("x", 0), -params.get("y", 0))
            array = HoloHG(
                params.get("m", 0), params.get("n", 0), params.get("w0", 0.2),
                LA=params.get("LA", 0.2) / 100, SLM_Pix=resolution, position=pos
            )
            selected_cmap = params.get("Cmap", "gray")

        elif content_type == "Random Noise":
            array = np.random.normal(0.5, 0.1, resolution)

        elif content_type == "Gradient":
            array = np.linspace(0, 1, resolution[1])[None, :] * np.ones((resolution[0], 1))

        elif content_type == "Zeros":
            array = np.zeros(resolution)

        elif content_type == "None":
            # print(f"[DEBUG] Closing display for Screen {screen_index}")
            self.close_screen(screen_index)
            return

        # ✅ Retrieve stored colormap
        params = self.parameters[screen_index].get(content_type.lower().replace(" ", "_"), {})
        selected_cmap = params.get("Cmap", "gray")

        # ✅ Debug Print to Check Colormap Selection
      # print(f"[DEBUG] Applying colormap '{selected_cmap}' to Screen {screen_index} for {content_type}")

        # ✅ Ensure `show_screen()` is called
        if array is not None:
            self.show_screen(screen_index, array, selected_cmap)
        else:
            # print(f"[DEBUG] No valid array generated for Screen {screen_index}")


            # ✅ Ensure colormap is applied correctly
            params = self.parameters[screen_index].get(content_type.lower().replace(" ", "_"), {})
            selected_cmap = params.get("Cmap", "gray")  # ✅ Get colormap from parameters if available

            # ✅ Fix: Ensure `show_screen()` is always called for valid arrays
            if array is not None:
                # print(f"[DEBUG] Displaying {content_type} on Screen {screen_index} with colormap '{selected_cmap}'")  # Debug
                self.show_screen(screen_index, array, selected_cmap)
            #else:
            #     print(f"[DEBUG] No valid array generated for Screen {screen_index}")  # Debug

    def show_screen(self, screen_index, array, selected_cmap):
        """
        Show or update the screen with the given content.
        """
        screens = QApplication.screens()
        if 0 <= screen_index < len(screens):
            screen_geometry = screens[screen_index].geometry()
            # print(f"[DEBUG] Displaying on Screen {screen_index}, Resolution: {screen_geometry.width()}x{screen_geometry.height()}")

        if screen_index in self.displays:
            # print(f"[DEBUG] Updating existing display on Screen {screen_index} with colormap '{selected_cmap}'")
            self.displays[screen_index].update_array(array, Cmap_Dict[selected_cmap])  # ✅ Pass colormap when updating
        else:
            # print(f"[DEBUG] Creating new display for Screen {screen_index} with colormap '{selected_cmap}'")
            
            # ✅ Use the passed `selected_cmap` instead of reloading from parameters
            display = ArrayDisplay(array, Cmap_Dict[selected_cmap], screen_index=screen_index)
            self.displays[screen_index] = display

    def quit_application(self):
        # Close all display windows and quit the application
        for display in self.displays.values():
            display.close()
        self.close()
        QApplication.quit()

    def close_screen(self, screen_index):
        """
        Close the display window for the given screen index.
        """
        if screen_index in self.displays:
            # print(f"[DEBUG] Closing screen {screen_index}")  # ✅ Debug print
            self.displays[screen_index].close()
            del self.displays[screen_index]  # ✅ Remove from dictionary
