# -*- coding: utf-8 -*-
"""
SLMpy_GUI - Spatial Light Modulator (SLM) GUI

This script serves as the **entry point** for the SLMpy GUI application.

Project Structure:
SLMpy_GUI/
│── main.py               # Entry point for the application
│── gui.py                # GUI components and main window
│── display.py            # Handles display functions for multiple screens
│── holograms.py          # Functions related to generating holograms
│── optics.py             # Special functions (Zernike polynomials, Laguerre-Gaussian, Hermite-Gaussian, etc.)
│── propagation.py        # Propagation functions (Fresnel propagation, Fourier methods)
│── utils.py              # Utility functions (coordinate transformations, normalization)

Author: Manuel Ferrer (@mferrerg)
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui import MultiScreenController  # Import the GUI controller class

def main():
    """
    Initializes and runs the SLMpy GUI application.

    This function:
    1. Checks if a QApplication instance already exists (useful for environments like Spyder).
    2. Creates a QApplication instance if none exists.
    3. Instantiates the `MultiScreenController`, which manages the multi-screen GUI.
    4. Displays the GUI window.
    5. Starts the application's event loop.

    Notes:
    - The `QApplication.instance()` check prevents multiple conflicting instances in IDEs.
    - `app.exec_()` starts the Qt event loop, keeping the application running.
    - Unlike some Qt applications, we avoid `sys.exit(app.exec_())` to allow smooth closing.
    """
    app = QApplication.instance()  # ✅ Use existing QApplication instance if running in Spyder or IPython
    if app is None:
        app = QApplication(sys.argv)  # ✅ Create a new QApplication instance if none exists

    controller = MultiScreenController()  # ✅ Initialize the GUI controller
    controller.show()  # ✅ Display the GUI window

    app.exec_()  # ✅ Start the Qt event loop

# ✅ Run `main()` only if this script is executed directly
if __name__ == "__main__":
    main()
