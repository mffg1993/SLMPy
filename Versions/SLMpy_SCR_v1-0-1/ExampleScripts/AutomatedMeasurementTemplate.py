import sys
import numpy as np
import time
import threading
from PyQt5.QtWidgets import QApplication
from SLMnew import ScreenManager
from holograms import HoloHG  # Import hologram function
from pylablib.devices import Thorlabs

def run_SLM(): 
    """Initialize QApplication and display the hologram in the main thread."""


def run_motor():
    time.sleep(10)
    """Run motor in a separate thread without interfering with the GUI."""
    for ii in range(10):
        print("Motor is running")
        time.sleep(1)

app = QApplication.instance() or QApplication(sys.argv)
# Initialize the screen manager
screen_manager = ScreenManager()
resolutions = screen_manager.get_screen_resolutions()

# Ensure screen index 2 exists before setting the hologram
screen_index = 2 if 2 in resolutions else 1  # Default to screen 1 if screen 2 isn't available

# Create and set the hologram once (Static Display) on screen 2
hg_hologram = HoloHG(m=3, n=2, w0=0.5, LA=0.001, SLM_Pix=resolutions[screen_index])
screen_manager.add_screen(screen_index, hg_hologram)




t1 = threading.Thread(target=run_motor, name='t1')  # Only motor runs in separate thread

t1.start()





# Run the QApplication event loop in the main thread
app.exec_()
t1.join()
