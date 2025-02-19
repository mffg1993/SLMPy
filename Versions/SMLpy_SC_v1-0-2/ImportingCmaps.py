import os
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))  # Ensure saving in the same folder as the script

# Get the full path of the colormap subfolder
subfolder_path = os.path.join(script_dir, "Cmaps")

# Get all colormap files in the subfolder (assuming they end with .cmap)
cmap_files = [f for f in os.listdir(subfolder_path) if f.endswith(".cmap")]

# Dictionary to store the colormaps
Cmap_Dict = {}

# Load each colormap file and add it to the dictionary
for cmap_file in cmap_files:
    cmap_name = os.path.splitext(cmap_file)[0]  # Remove the .cmap extension
    cmap_path = os.path.join(subfolder_path, cmap_file)  # Full file path

    # Load colormap data from file
    cmap_data = np.loadtxt(cmap_path)

    # Convert to LinearSegmentedColormap and store in the dictionary
    Cmap_Dict[cmap_name] = LinearSegmentedColormap.from_list(cmap_name, cmap_data)

# Print to verify
#print("Loaded colormaps:", Cmap_Dict.keys())
