# SLMpy_GUI_v1-0-0

SLMpy_GUI_v1-0-0 is a Python-based graphical user interface for controlling a Spatial Light Modulator (SLM) to generate and display holograms. This version provides a multi-screen control system with support for various beam modes, including Laguerre-Gaussian and Hermite-Gaussian holograms, random noise patterns, and gradient fields.

## Features

- **Multi-Screen Control**: Manage multiple screens with different content types.
- **Beam Mode Generation**:
  - Laguerre-Gaussian (LG) Holograms
  - Hermite-Gaussian (HG) Holograms
- **Custom Display Options**:
  - Random Noise
  - Gradient Fields
  - Zero-filled Screens
- **Graphical Interface**:
  - Select content type for each screen
  - Adjustable parameters for beam modes
  - Live preview and fullscreen display

## Installation

### Prerequisites

Ensure you have Python 3 installed along with the required dependencies:

```bash
pip install numpy matplotlib pyqt5
```

### Running the Application

To launch the GUI, execute the following command:

```bash
python SLMpy_GUI_v1-0-0.py
```

## Usage

1. **Launch the GUI**: Start the program and select a screen configuration.
2. **Choose Content Type**: Assign different visual patterns to each screen.
3. **Adjust Parameters**: Modify settings such as beam waist, grating period, and mode indices.
4. **Display on Screens**: Preview and apply the settings to the screens.

## Features

- **Multi-Screen Control:** Capable of managing multiple screens. Autodetects the number of screens and their resolution.
- **Basic beam shaping:** Contains the basic beams that I typically used, but I expect to add more eventually
  - Laguerre-Gaussian Beams
  - Hermite-Gaussian Beams
  - Uniform zero-filled screen for alignment
  - Gradient
  - Random Noise


