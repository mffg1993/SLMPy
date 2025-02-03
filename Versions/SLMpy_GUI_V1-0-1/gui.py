from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox, QHBoxLayout, QPushButton, QApplication
)
from PyQt5.QtCore import Qt
from functools import partial
import numpy as np
from display import ArrayDisplay
from holograms import HoloLG, HoloHG
from config_dock import ConfigDock

class MultiScreenController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Screen Display Controller")  # Set the window title
        self.central_widget = QWidget()  # Create the central widget
        self.setCentralWidget(self.central_widget)  # Set the central widget

        # Dictionary to hold display objects for each screen
        self.displays = {}
        # List of available screens
        self.screens = QApplication.screens()
        # Dictionary to hold parameters for each screen
        self.parameters = {i: {"type": None} for i in range(len(self.screens))}
        # Dictionary to hold configuration docks for each screen
        self.config_docks = {}

        # Widgets configuration for different content types
        self.widgets = {
            "LG Hologram": [
                {"name": "l", "type": "spinbox", "range": (-10, 10), "default": 0},
                {"name": "p", "type": "spinbox", "range": (0, 10), "default": 0},
                {"name": "w0", "type": "doublespinbox", "range": (0.1, 5.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "LA", "type": "doublespinbox", "range": (0.1, 1.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "x", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01},
                {"name": "y", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01},
            ],
            "HG Hologram": [
                {"name": "l", "type": "spinbox", "range": (-10, 10), "default": 0},
                {"name": "p", "type": "spinbox", "range": (0, 10), "default": 0},
                {"name": "w0", "type": "doublespinbox", "range": (0.1, 5.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "LA", "type": "doublespinbox", "range": (0.1, 1.0), "default": 0.2, "SingleStep": 0.01},
                {"name": "x", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01},
                {"name": "y", "type": "doublespinbox", "range": (-6, 6), "default": 0.0, "SingleStep": 0.01}
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

        # Initialize the user interface
        self.init_ui()
        # Initialize configuration docks for each screen
        self.init_config_docks()

    def init_ui(self):
        # Set up the main layout
        layout = QVBoxLayout(self.central_widget)
        instructions = QLabel("Select content for each screen and configure options.")
        layout.addWidget(instructions)

        # Create controls for each screen
        self.screen_controls = []
        for idx, screen in enumerate(self.screens):
            screen_layout = QHBoxLayout()
            label = QLabel(f"Screen {idx}:")
            combobox = QComboBox()

            # Automatically adds new features once they are added to the widgets dictionary            
            combobox.addItems(self.widgets.keys())
            
            # Setting the default value to "None"
            combobox.setCurrentText("None")

            combobox.currentIndexChanged.connect(partial(self.update_content, idx, combobox))
            screen_layout.addWidget(label)
            screen_layout.addWidget(combobox)
            self.screen_controls.append(combobox)
            layout.addLayout(screen_layout)

        # Add a quit button
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
            # print(f"[DEBUG] Initializing parameters for Screen {screen_index}")  # ✅ Debug print
            self.parameters[screen_index] = {"type": None}

        content_type = self.parameters[screen_index].get("type", None)
        # print(f"[DEBUG] Updating display for Screen {screen_index}, Type: {content_type}")  # ✅ Debug print

        if content_type is None:
            # print(f"[DEBUG] No valid content type selected for Screen {screen_index}")
            return  # ✅ Exit if no content type is selected

        step1 = self.screens[screen_index]
        resolution = (step1.geometry().width(), step1.geometry().height())

        if content_type == "LG Hologram":
            params = self.parameters[screen_index].get("lg_hologram", {})
            # print(f"[DEBUG] Using LG Hologram params: {params}")  # ✅ Debug print
            pos=(-params.get("x",0),-params.get("y",0))
            array = HoloLG(params.get("l", 0), params.get("p", 0), params.get("w0", 0.2), LA=params.get("LA",0.2)/100, SLM_Pix=resolution, position=pos)

        elif content_type == "HG Hologram":
            params = self.parameters[screen_index].get("hg_hologram", {})
            # print(f"[DEBUG] Using HG Hologram params: {params}")  # ✅ Debug print
            pos=(-params.get("x",0),-params.get("y",0))
            array = HoloHG(params.get("m", 0), params.get("n", 0), params.get("w0", 0.2), LA=params.get("LA",0.2)/100, SLM_Pix=resolution, position=pos)

        elif content_type == "Random Noise":
            array = np.random.normal(0.5, 0.1, resolution)

        elif content_type == "Gradient":
            array = np.linspace(0, 1, resolution[1])[None, :] * np.ones((resolution[0], 1))

        elif content_type == "None":
            # print(f"[DEBUG] Closing display for Screen {screen_index}")  # ✅ Debug print
            self.close_screen(screen_index)
            return

        elif content_type == "Zeros":
            array = np.zeros(resolution)

        if array is not None:
            # print(f"[DEBUG] Sending new array to Screen {screen_index}")  # ✅ Debug print
            self.show_screen(screen_index, array)
        else:
            # print(f"[DEBUG] No array generated for Screen {screen_index}")  # ✅ Debug print


    def show_screen(self, screen_index, array):
        """
        Show or update the screen with the given content.
        """
        screens = QApplication.screens()
        if 0 <= screen_index < len(screens):
            screen_geometry = screens[screen_index].geometry()
            print(f"[DEBUG] Displaying on Screen {screen_index}, Resolution: {screen_geometry.width()}x{screen_geometry.height()}")

        if screen_index in self.displays:
            print(f"[DEBUG] Updating existing display on Screen {screen_index}")
            self.displays[screen_index].update_array(array)  
        else:
            print(f"[DEBUG] Creating new display for Screen {screen_index}")
            display = ArrayDisplay(array, screen_index=screen_index)
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
