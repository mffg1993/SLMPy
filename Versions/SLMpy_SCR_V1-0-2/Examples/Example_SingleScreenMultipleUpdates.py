import sys
import time
import threading
import numpy as np
from PyQt5.QtWidgets import QApplication
from slm import SLM, get_screen_info, load_colormaps
from holograms import HoloLG
from PyQt5.QtCore import QTimer


"""
CHECKED:
    - New SLM class to simplyfy the layout. 
    - Multidisplay support works in Windows
    - Updates using Qtime works! 
    - Automatic screen resolution detection
    - Custom Color maps work

NEEDS: 
    - Correct Holograms
    - Add Amplitude MaskControl

"""
# Loads custom colormaps +"gray". The .cmap files should be in the Cmaps folder. 
cmap_dict = load_colormaps()
cmap_list = list(cmap_dict.keys())

# print(cmap_list) # Check if the colormaps are loaded correctly


# Retrieves the resolution of the available screens
res_screen = get_screen_info()

# print(res_screen[1]) # Check if the screen resolution is correct

# Initialize QApplication in the main thread
app = QApplication.instance() or QApplication(sys.argv)

    # Generate holograms
holo1 = HoloLG(l=1, p=0, w0=0.05, LA=0.001, SLM_Pix=res_screen[1])  # First hologram

# Assign holograms to screens
Screen1 = SLM(1, holo1,cmap_dict['PlutoC'])  # Screen 1 with holo1 using the Pluto colormap

# ===========
# Loop Control for more than one hologram
# ===========

waist=np.linspace(0.05,0.1,10)

# List of predefined holograms to display sequentially
holograms = [HoloLG(l=1, p=0, w0=w, LA=0.001, SLM_Pix=(1920, 1080)) for w in waist]


# Time interval (in milliseconds) between updates (5 seconds)
update_interval = 1000  # 1000 ms = 1 seconds


def update_sequence(index=0):
    """
    Function to update the SLM screen with the next hologram in the list.
    
    Parameters:
        - index (int): The current index of the hologram to be displayed.
    
    Behavior:
        - If `index` is within the range of `holograms`, update the screen with the corresponding hologram.
        - Schedule the next update after `update_interval` milliseconds.
        - Stops automatically when all holograms have been displayed.
    """
    if index < len(holograms):  # Ensure index is within bounds
        Screen1.update(holograms[index])  # Update the screen with the current hologram
        
        # Schedule the next hologram update after `update_interval` milliseconds
        QTimer.singleShot(update_interval, lambda: update_sequence(index + 1))

# Start the sequence: Display the first hologram after an initial delay of 5 seconds
QTimer.singleShot(1000, lambda: update_sequence(0))


# Start the GUI event loop
sys.exit(app.exec_())


