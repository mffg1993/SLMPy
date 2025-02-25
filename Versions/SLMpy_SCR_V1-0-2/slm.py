import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
from matplotlib.colors import LinearSegmentedColormap

# Ensure QApplication is created before any GUI elements
app = QApplication.instance() or QApplication([])

class SLM(QMainWindow):
    def __init__(self, screen_index=0, hologram=None, Cmap='gray'):
        """
        Initializes an SLM screen window.

        Parameters:
            - screen_index (int): The index of the screen.
            - hologram (numpy.ndarray): The precomputed hologram to display.
        """
        super().__init__()

        self.screen_index = screen_index
        self.cmap = Cmap
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
        self.ax.imshow(resized_array, cmap=self.cmap, aspect="auto")
        self.ax.set_axis_off()
        self.canvas.draw()

    def update(self, new_hologram):
        """Updates the screen with a new hologram."""
        self.display(new_hologram)


# ========
# Getting the information of the screens available
# ========

def get_screen_info():
    """
    Fetches available screens and their resolutions.

    Returns:
        - A list containing screen index, resolution, and name.
    """
    app = QApplication.instance() or QApplication([])  # Ensure QApplication exists
    screen_list = QApplication.screens()

    return [(screen.geometry().width(), screen.geometry().height())
  
        for i, screen in enumerate(screen_list)
    ]


#====
# Loading colormaps
#====

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

