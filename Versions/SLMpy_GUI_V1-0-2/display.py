"""
ArrayDisplay - Full-Screen Image Display for Multi-Screen Setup

This module defines the `ArrayDisplay` class, which is responsible for displaying 2D arrays as images
on full-screen windows using Matplotlib. The display supports dynamic updates with different colormaps.

Author: Manuel Ferrer (@mferrerg)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt

class ArrayDisplay(QMainWindow):
    """
    Handles the full-screen display of a 2D array using Matplotlib.
    
    This class creates a frameless window that displays a NumPy array as an image
    and allows dynamic updates with different colormaps.
    """

    def __init__(self, array, Cmap, screen_index):
        """
        Initializes the display window.

        Parameters:
        array : np.ndarray
            The 2D NumPy array to be displayed as an image.
        Cmap : str
            The colormap to apply to the image.
        screen_index : int
            The index of the screen on which the image is displayed.
        """
        super().__init__()
        self.setWindowTitle(f'Display Array on Screen {screen_index}')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create a figure and axis for plotting
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Fill figure
        self.ax.set_axis_off()

        # Convert input array to real values and display with colormap
        array_real = np.abs(array)
        self.image = self.ax.imshow(array_real, cmap=Cmap, aspect='auto')

        # Add Matplotlib figure to the PyQt layout
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        # Set frameless full-screen window
        self.setWindowFlags(Qt.FramelessWindowHint)
        screens = QApplication.screens()
        if 0 <= screen_index < len(screens):
            screen_geometry = screens[screen_index].geometry()
            self.setGeometry(screen_geometry)

        self.showFullScreen()

    def update_array(self, new_array, cmap):
        """
        Updates the displayed array with new data and applies a new colormap.

        Parameters:
        new_array : np.ndarray
            The updated 2D array to be displayed.
        cmap : str
            The new colormap to apply to the updated image.
        """
        self.image.set_data(new_array)
        self.image.set_cmap(cmap)
        self.canvas.draw()
