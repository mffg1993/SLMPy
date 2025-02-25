"""
Example Python Script for SLM Hologram Display

This script demonstrates how to use a Spatial Light Modulator (SLM) to display Hermite-Gaussian (HG) and Laguerre-Gaussian (LG) holograms.
It initializes an SLM screen manager, retrieves available screen resolutions, and manually computes holograms.
The script also schedules automatic updates to swap displayed holograms after predefined time intervals using PyQt5's QTimer.

Features:
- Generates and displays HG and LG holograms using a custom SLM screen manager.
- Supports manual hologram updates on different screens after a time delay.
- Uses PyQt5 for GUI event loop management.
- Ensures modularity and expandability for research applications in optics and physics.

Requirements:
- PyQt5 for GUI management.
- Custom modules `SLMnew` and `holograms`.

Author: Manuel Ferrer 
Date: 19/02/2025
License: GNU 3.0 
"""
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from slm import ScreenManager
from holograms import HoloHG, HoloLG  # Import hologram functions
from PyQt5.QtCore import QTimer


# ==========================
# QApplication Setup
# ==========================

# Ensure QApplication is created before any GUI elements
app = QApplication.instance() or QApplication(sys.argv)

# ==========================
# SLM Hologram Setup
# ==========================

# Initialize the screen manager
screen_manager = ScreenManager()

# Retrieve available screen resolutions (using screen index as a key)
resolutions = screen_manager.get_screen_resolutions()

# Compute holograms manually with predefined parameters
hg_hologram = HoloHG(m=3, n=2, w0=0.5, LA=0.001, SLM_Pix=resolutions[1])  # HG Mode
lg_hologram = HoloLG(l=2, p=1, w0=0.6, LA=0.0015, SLM_Pix=resolutions[1])  # LG Mode

# Manually add screens with holograms
screen_manager.add_screen(1, hg_hologram)  # Display HG hologram on screen 1
# screen_manager.add_screen(2, lg_hologram)  # Uncomment to display LG hologram on screen 2

# ==========================
# Hologram Update Functionality
# ==========================

def update_screen(index,U):
    """
    Updates screen 1 with a new hologram.
    Parameters:
    - U: New hologram object to be displayed.
    """
    print("Updating Screen 1...")
    screen_manager.update_screen(1, U)

# Set timers for updating the screen with different holograms at specific intervals
QTimer.singleShot(3000, lambda: update_screen(index,lg_hologram))  # Update to LG hologram after 3 seconds
QTimer.singleShot(5000, lambda: update_screen(index,hg_hologram))  # Revert to HG hologram after 5 seconds

# ==========================
# Running the Application
# ==========================

# Start the PyQt5 event loop to keep the application running
sys.exit(app.exec_())
