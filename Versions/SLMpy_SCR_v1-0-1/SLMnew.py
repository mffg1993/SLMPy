import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt

# Ensure QApplication is created before any GUI elements
app = QApplication.instance() or QApplication([])

# Screen Controller Class
class SLMScreen(QMainWindow):
    def __init__(self, screen_index=0, hologram=None):
        """
        Initializes an SLM screen window.

        Parameters:
            - screen_index (int): The index of the screen.
            - hologram (numpy.ndarray): The precomputed hologram to display.
        """
        super().__init__()

        self.screen_index = screen_index
        self.screens = QApplication.screens()

        if self.screen_index >= len(self.screens):
            raise ValueError(f"Screen {self.screen_index} is not available. Available screens: {len(self.screens)}")

        # Get screen resolution
        self.screen_geometry = self.screens[self.screen_index].geometry()
        self.resolution = (self.screen_geometry.width(), self.screen_geometry.height())

        # Set up matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(self.resolution[0] / 100, self.resolution[1] / 100))
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax.set_axis_off()
        self.canvas = FigureCanvas(self.figure)

        # Configure PyQt window
        self.setCentralWidget(self.canvas)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(self.screen_geometry)
        self.showFullScreen()

        # Display the initial hologram (if provided)
        if hologram is not None:
            self.display(hologram)

    def display(self, array):
        """Displays the given hologram pattern on the screen."""
        scale_x = self.resolution[1] / array.shape[0]
        scale_y = self.resolution[0] / array.shape[1]
        resized_array = np.kron(array, np.ones((int(scale_x), int(scale_y))))  # Resize array

        self.ax.clear()
        self.ax.imshow(resized_array, cmap="gray", aspect="auto")
        self.ax.set_axis_off()
        self.canvas.draw()

# **Screen Manager: Handles Individual Screens Only**
class ScreenManager:
    def __init__(self):
        """Initializes an empty screen manager."""
        self.screens = {}
        

    def add_screen(self, screen_index, hologram):
        """Adds a new screen and displays the initial hologram."""
        try:
            self.screens[screen_index] = SLMScreen(screen_index=screen_index, hologram=hologram)
        except ValueError as e:
            print(e)

    def update_screen(self, screen_index, hologram):
        """Updates a single screen with a new hologram."""
        if screen_index in self.screens:
            self.screens[screen_index].display(hologram)
        else:
            print(f"Screen {screen_index} not found.")

    def get_screen_resolutions(self):
        """Returns a dictionary with the resolutions of all available screens."""
        screen_list = QApplication.screens()
        resolutions = {i: (screen.geometry().width(), screen.geometry().height()) for i, screen in enumerate(screen_list)}
        return resolutions