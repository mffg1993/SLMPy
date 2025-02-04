import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Define the resolution of the colormap
num_colors = 256

# Generate input values from -1 to 1
i_vals = np.linspace(-1, 1, num_colors)

# Define the colormap function for THORLABS 780NM
Thorlabs_values = np.abs(123 + 69.5 * i_vals - 29.8 * i_vals**2 + 19.5 * i_vals**3) / 255

# Define the colormap function for PLuto 405NM
Pluto_values = np.abs(33.1 + 51.7 * i_vals - 2.57 * i_vals**2 - 14.3 * i_vals**3 +
                      16.7 * i_vals**4 + 5.81 * i_vals**5 - 4.02 * i_vals**6) / 255  # Normalize to 0-1 range

# Ensure the shape is (256, 3) for an RGB colormap (only modifying the green channel)
custom_Thorlabs_cmap_data = np.zeros((num_colors, 3))
custom_Thorlabs_cmap_data[:, 1] = Thorlabs_values  # Only modifying the green channel

custom_Pluto_cmap_data = np.zeros((num_colors, 3))
custom_Pluto_cmap_data[:, 1] = Pluto_values  # Only modifying the green channel

# Create the colormap
Thorlabs_cmap = LinearSegmentedColormap.from_list("Thorlabs", custom_Thorlabs_cmap_data)
Pluto_cmap = LinearSegmentedColormap.from_list("Pluto", custom_Pluto_cmap_data)

# Save the custom colormaps to text files (formatted correctly)
np.savetxt("ThorlabsC.cmap", custom_Thorlabs_cmap_data, fmt="%.6f", delimiter=" ")
np.savetxt("PlutoC.cmap", custom_Pluto_cmap_data, fmt="%.6f", delimiter=" ")

print("Colormaps saved successfully!")
