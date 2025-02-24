# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:40:35 2025

@author: mferrerg
"""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from SLMnew import ScreenManager
from holograms import HoloHG, HoloLG  # Import hologram functions
from PyQt5.QtCore import QTimer


# Ensure QApplication is created before any GUI elements
app = QApplication.instance() or QApplication(sys.argv)


# Initialize the screen manager (NO FOR LOOP)
screen_manager = ScreenManager()
    
# It request a dictionary with the resolutions of each available screen using the screen's index as key
resolutions=screen_manager.get_screen_resolutions()

# Compute holograms manually
hg_hologram = HoloHG(m=3, n=2, w0=0.5, LA=0.001, SLM_Pix=resolutions[1])
lg_hologram = HoloLG(l=2, p=1, w0=0.6, LA=0.0015, SLM_Pix=resolutions[1])

# Manually add screens
screen_manager.add_screen(1, hg_hologram)
#screen_manager.add_screen(2, lg_hologram)

# Example: Update screen 1 to a different HG hologram after 5 seconds

def update_screenapp(U): 
    print("Updating Screen 1...")
    new_hg_hologram = U
    screen_manager.update_screen(1,U)


def update_screen1(): 
    print("Updating Screen 1...")
    new_hg_hologram = HoloHG(m=5, n=3, w0=0.6, LA=0.02, SLM_Pix=(1024, 780))
    screen_manager.update_screen(1, new_hg_hologram)

timer = QTimer()
timer.singleShot(3000, lambda: update_screenapp(lg_hologram))  # Update after 5 seconds

timer.singleShot(5000, lambda: update_screenapp(hg_hologram))  # Update after 5 seconds

# Run the QApplication event loop
sys.exit(app.exec_())
