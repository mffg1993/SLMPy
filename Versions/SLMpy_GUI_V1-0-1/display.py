import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt

class ArrayDisplay(QMainWindow):
    def __init__(self, array, screen_index):
        super().__init__()
        self.setWindowTitle(f'Display Array on Screen {screen_index}')  # Set the window title
        self.central_widget = QWidget()  # Create the central widget
        self.setCentralWidget(self.central_widget)  # Set the central widget
        self.layout = QVBoxLayout(self.central_widget)  # Use QVBoxLayout for the layout

        self.fig, self.ax = plt.subplots()  # Create a figure and axis for plotting
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Adjust the subplot to fill the figure
        self.ax.set_axis_off()  # Turn off the axis

        array_real = np.abs(array)  # Convert to real values
        self.image = self.ax.imshow(array_real, cmap='gray', aspect='auto')  # Display the array as an image

        self.canvas = FigureCanvas(self.fig)  # Create a canvas for the figure
        self.layout.addWidget(self.canvas)  # Add the canvas to the layout

        self.setWindowFlags(Qt.FramelessWindowHint)  # Set the window to be frameless
        screens = QApplication.screens()  # Get the list of screens
        if 0 <= screen_index < len(screens):
            screen_geometry = screens[screen_index].geometry()  # Get the geometry of the specified screen
            self.setGeometry(screen_geometry)

        self.showFullScreen()

    def update_array(self, new_array):
        """
        Update the displayed array with new data.
        """
        # ✅ Ensure real values before updating
        self.image.set_data(new_array)
        self.canvas.draw()
        print(f"[DEBUG] Updated display with new data on screen {self.windowTitle()}")
