"""
Example Python Script for SLM Hologram Display and Measurement Automation

This script demonstrates how to use a Spatial Light Modulator (SLM) to display Hermite-Gaussian (HG) holograms 
and simultaneously run a separate measurement process using a motor. The script is designed to integrate with
PyQt5 for GUI handling and supports multi-threading to ensure smooth operation without blocking the UI.

Features:
- Generates and displays an HG hologram using a custom SLM screen manager.
- Runs a motor control simulation in a separate thread to mimic a real-time measurement setup.
- Uses PyQt5 for GUI event loop management.
- Ensures modularity and expandability for research applications in optics and physics.

Requirements:
- PyQt5 for GUI management.
- pylablib for interfacing with Thorlabs devices.
- Custom modules `slm` and `holograms`.

Author: Manuel Ferrer 
Date: 25/02/2025
License: GNU 3.0
"""

import sys
import numpy as np
import time
import threading
from PyQt5.QtWidgets import QApplication
from slm import ScreenManager
from holograms import HoloHG  # Import hologram function
from pylablib.devices import Thorlabs

# ==========================
# Measurement Setup
# ==========================

def measurement_step():
    """
    Simulates a measurement process by running a motor in a separate thread.
    This function introduces a delay and then runs the motor loop for 10 iterations.
    Each iteration prints a message and waits for 1 second.
    """
    time.sleep(10)  # Initial delay before the measurement starts (simulating setup time)
    
    for ii in range(10):  # Loop to simulate motor running for 10 seconds
        print("Motor is running")  # Print status update
        time.sleep(1)  # Introduce a delay of 1 second per iteration

# ==========================
# SLM Hologram Setup
# ==========================

# Check if a QApplication instance already exists; if not, create one
app = QApplication.instance() or QApplication(sys.argv)

# Initialize the ScreenManager, which manages the Spatial Light Modulator (SLM)
screen_manager = ScreenManager()

# Retrieve the available screen resolutions (used to determine where to place the hologram)
resolutions = screen_manager.get_screen_resolutions()

# Determine the screen index for the SLM display.
# If a screen with index 2 exists, use it; otherwise, default to screen index 1.
screen_index = 2 if 2 in resolutions else 1  # Ensures compatibility if screen 2 is not available

# Generate a Hermite-Gaussian (HG) hologram with specific parameters:
# - m=3, n=2: Defines the HG mode numbers
# - w0=0.5: Beam waist size
# - LA=0.001: Scale parameter related to the beam
# - SLM_Pix: Uses the resolution of the selected screen
hg_hologram = HoloHG(m=3, n=2, w0=0.5, LA=0.001, SLM_Pix=resolutions[screen_index])

# Add the generated hologram to the selected screen using the screen manager
screen_manager.add_screen(screen_index, hg_hologram)

# ==========================
# Running the Complete Measurement
# ==========================

# Create a new thread for the motor control to prevent blocking the GUI
# However, the function name `run_motor` is not defined in this script; it should be `measurement_step`.
t1 = threading.Thread(target=measurement_step, name='t1')  # Runs the motor function in a separate thread

# Start the measurement thread (motor operation)
t1.start()

# Execute the PyQt5 event loop in the main thread to ensure GUI responsiveness
app.exec_()

# Wait for the measurement thread to complete before exiting the script
t1.join()

