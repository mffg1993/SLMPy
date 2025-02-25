import sys
import time
import threading
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
holo2 = HoloLG(l=2, p=1, w0=0.05, LA=0.001, SLM_Pix=res_screen[1])  # Second hologram
#holo3 = HoloLG(l=2, p=1, w0=0.05, LA=0.001, SLM_Pix=res_screen[2])  # Second hologram


# Assign holograms to screens
#Screen1 = SLM(1, holo1)  # Screen 1 with holo1 using the gray colormap as default

Screen1 = SLM(1, holo1,cmap_dict['PlutoC'])  # Screen 1 with holo1 using the Pluto colormap
#Screen2 = SLM(2, holo3)  # Screen 2 with holo2

# Update the screen with a new hologram after 5 seconds
QTimer.singleShot(5000, lambda: Screen1.update(holo2))

# Start the GUI event loop
sys.exit(app.exec_())

