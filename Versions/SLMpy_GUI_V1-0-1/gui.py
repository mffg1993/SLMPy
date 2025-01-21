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
        self.setWindowTitle("Multi-Screen Display Controller")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.displays = {}
        self.screens = QApplication.screens()
        self.parameters = {i: {"type": None} for i in range(len(self.screens))}
        self.config_docks = {}

        self.widgets = {
            "LG Hologram": [
                {"name": "l", "type": "spinbox", "range": (-10, 10), "default": 0},
                {"name": "p", "type": "spinbox", "range": (0, 10), "default": 0},
                {"name": "w0", "type": "doublespinbox", "range": (0.1, 10.0), "default": 0.2},
            ],
            "HG Hologram": [
                {"name": "m", "type": "spinbox", "range": (-10, 10), "default": 1},
                {"name": "n", "type": "spinbox", "range": (-10, 10), "default": 0},
            ],
        }

        self.init_ui()
        self.init_config_docks()

    def init_ui(self):
        layout = QVBoxLayout(self.central_widget)
        instructions = QLabel("Select content for each screen and configure options.")
        layout.addWidget(instructions)

        self.screen_controls = []
        for idx, screen in enumerate(self.screens):
            screen_layout = QHBoxLayout()
            label = QLabel(f"Screen {idx}:")
            combobox = QComboBox()
            combobox.addItems(["None", "Random Noise", "Gradient", "LG Hologram", "HG Hologram"])
            combobox.currentIndexChanged.connect(partial(self.update_content, idx, combobox))
            screen_layout.addWidget(label)
            screen_layout.addWidget(combobox)
            self.screen_controls.append(combobox)
            layout.addLayout(screen_layout)

        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.quit_application)
        layout.addWidget(quit_button)

    def init_config_docks(self):
        for idx in range(len(self.screens)):
            self.config_docks[idx] = ConfigDock(self, idx)

    def update_content(self, screen_index, combobox):
        content_type = combobox.currentText()
        if screen_index not in self.parameters:
            self.parameters[screen_index] = {"type": None}
        self.parameters[screen_index]["type"] = content_type

        if content_type in self.widgets:
            self.config_docks[screen_index].update_dock(content_type, self.widgets[content_type])
        else:
            self.config_docks[screen_index].dock.hide()

        self.update_display(screen_index)

    def update_display(self, screen_index):
        if screen_index not in self.parameters:
            self.parameters[screen_index] = {"type": None}
        content_type = self.parameters[screen_index].get("type", None)
        
        step1 = self.screens[screen_index]
        resolution=(step1.geometry().width(),step1.geometry().height())

        #resolution = (1080, 1920)
z        #array = None

        if content_type == "LG Hologram":
            params = self.parameters[screen_index].get("lg_hologram", {})
            array = HoloLG(params.get("l", 0), params.get("p", 0), params.get("w0", 0.2), SLM_Pix=resolution)

        elif content_type == "HG Hologram":
            params = self.parameters[screen_index].get("hg_hologram", {})
            array = HoloHG(params.get("m", 0), params.get("n", 0), params.get("w0", 0.2), SLM_Pix=resolution)

        elif content_type == "Random Noise":
            array = np.random.normal(0.5, 0.1, resolution)

        elif content_type == "Gradient":
            array = np.linspace(0, 1, resolution[1])[None, :] * np.ones((resolution[0], 1))

        elif content_type == "None":
            array = np.zeros(resolution)

        if array is not None:
            array = np.abs(array)  # Ensure real values before displaying
            self.show_screen(screen_index, array)

    def show_screen(self, screen_index, array):
        screens = QApplication.screens()
        if 0 <= screen_index < len(screens):
            screen_geometry = screens[screen_index].geometry()
            print(f"[DEBUG] Displaying on Screen {screen_index}, Resolution: {screen_geometry.width()}x{screen_geometry.height()}")

        if screen_index in self.displays:
            self.displays[screen_index].update_array(array)
        else:
            display = ArrayDisplay(array, screen_index=screen_index)
            self.displays[screen_index] = display

    def quit_application(self):
        for display in self.displays.values():
            display.close()
        self.close()
        QApplication.quit()

