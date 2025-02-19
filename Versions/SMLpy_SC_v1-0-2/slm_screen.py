import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from scipy.ndimage import zoom  # For resizing holograms

# Ensure QApplication is created only once
app = QApplication.instance() or QApplication(sys.argv)

# Function to create a hologram (Hermite-Gaussian) with correct resolution
def HoloHG(m, n, w0, LA=0.005, maxx=1, resolution=(1920, 1080), position=(0, 0)):
    X = np.linspace(-maxx, maxx, resolution[0]) + position[0]
    Y = -np.linspace(-maxx, maxx, resolution[1]) + position[1]
    xx, yy = np.meshgrid(X, Y)
    A = np.exp(-(xx**2 + yy**2) / w0**2) * np.exp(-1j * m * xx) * np.exp(-1j * n * yy)
    return np.angle(A)

# Screen Controller Class
class SLMScreen(QMainWindow):
    """
    A class to control and display holograms on an external screen using matplotlib.
    """

    def __init__(self, screen_index=0):
        """
        Initializes an SLM screen object.

        Parameters:
            screen_index (int): The index of the screen to use.
        """
        super().__init__()

        self.screen_index = screen_index
        self.screens = QApplication.screens()
        self.cmap = "gray"  # Default colormap

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
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove window borders
        self.setGeometry(self.screen_geometry)  # Force exact screen size
        self.showFullScreen()  # Ensure full-screen mode

    def set_cmap(self, cmap_name):
        """
        Sets the colormap for displaying holograms.

        Parameters:
            cmap_name (str): The name of the matplotlib colormap (e.g., "jet", "viridis", "hot", "gray").
        """
        if cmap_name in plt.colormaps():
            self.cmap = cmap_name
            print(f"Colormap changed to: {self.cmap}")
        else:
            print(f"Invalid colormap name: {cmap_name}. Available colormaps: {plt.colormaps()}")

    def display(self, array):
        """
        Displays the given hologram pattern on the screen, resizing it to match the screen resolution.

        Parameters:
            array (np.ndarray): The image or hologram to display.
        """
        # Resize array to match screen resolution
        scale_x = self.resolution[1] / array.shape[0]
        scale_y = self.resolution[0] / array.shape[1]
        resized_array = zoom(array, (scale_x, scale_y))

        self.ax.clear()
        self.ax.imshow(resized_array, cmap=self.cmap, aspect="auto")
        self.ax.set_axis_off()
        self.canvas.draw()

    def clear(self):
        """
        Clears the screen.
        """
        self.display(np.zeros(self.resolution))

    def hold(self):
        """
        Keeps the window open until manually closed.
        """
        print("Press Ctrl+C or manually close the window to exit.")
        app.exec_()

    def close(self):
        """
        Closes the SLM screen.
        """
        super().close()
        app.quit()
