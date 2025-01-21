import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt

class ArrayDisplay(QMainWindow):
    def __init__(self, array, screen_index):
        super().__init__()
        self.setWindowTitle(f'Display Array on Screen {screen_index}')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax.set_axis_off()

        array_real = np.abs(array)
        self.image = self.ax.imshow(array_real, cmap='gray', aspect='auto')

        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        self.setWindowFlags(Qt.FramelessWindowHint)
        screens = QApplication.screens()
        if 0 <= screen_index < len(screens):
            screen_geometry = screens[screen_index].geometry()
            self.setGeometry(screen_geometry)

        self.showFullScreen()
