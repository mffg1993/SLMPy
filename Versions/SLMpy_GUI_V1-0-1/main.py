# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 16:50:19 2025

@author: mferrerg

SLMpy_GUI/
│── main.py               # Entry point for the application
│── gui.py                # GUI components and main window
│── display.py            # Handles display functions for multiple screens
│── holograms.py          # Functions related to generating holograms
│── optics.py             # Special functions (Zernike polynomials, Laguerre-Gaussian, Hermite-Gaussian, etc.)
│── propagation.py        # Propagation functions (Fresnel propagation, Fourier methods)
│── utils.py              # Utility functions (coordinate transformations, normalization)

"""

import sys
from PyQt5.QtWidgets import QApplication
from gui import MultiScreenController

def main():
    """
    Main function to run the application.
    """
    app = QApplication.instance()  # Use existing QApplication instance if running in Spyder
    if app is None:
        app = QApplication(sys.argv)
    controller = MultiScreenController()
    controller.show()
    app.exec_()  # Do not use sys.exit(app.exec_())

if __name__ == "__main__":
    main()

