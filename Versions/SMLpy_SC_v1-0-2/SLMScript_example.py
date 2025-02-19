from slm_screen import SLMScreen
from holograms import HoloHG
from ImportingCmaps import Cmap_Dict

# Initialize screen object
screen1 = SLMScreen(screen_index=0)

# Print available custom colormaps (optional)
print("Available custom colormaps:", list(Cmap_Dict.keys()))

# Select a custom colormap (replace with the name of your actual .cmap file, without extension)
custom_cmap_name = "PlutoC"  # Change this to match your file name

if custom_cmap_name in Cmap_Dict:
    custom_cmap = Cmap_Dict[custom_cmap_name]
else:
    print(f"Warning: Custom colormap '{custom_cmap_name}' not found! Using default.")
    custom_cmap = "gray"  # Fallback colormap

# Generate a Hermite-Gaussian (HG) Hologram
HG_params = {
    "m": 3,
    "n": 2,
    "w0": 0.5,
    "LA": 0.01,
    "SLM_Pix": screen1.resolution,  # Ensure resolution matches screen size
}
hologram = HoloHG(**HG_params)

# Display the hologram with the custom colormap
screen1.ax.imshow(hologram, cmap=custom_cmap, aspect="auto")  # Manually apply colormap
screen1.canvas.draw()  # Refresh the display

# Hold the display until manually closed
screen1.hold()
