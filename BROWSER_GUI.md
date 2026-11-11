# SLMPy Browser (experimental)

A **local** web-app-style GUI for hologram previews and multiple SLM screens, with optional NumPy/CuPy GPU acceleration. This is an additive prototype: the historical `Versions/` programs are unchanged.

## Installation (Windows / Anaconda)

Open Anaconda Prompt, preferably on the computer connected to the SLMs:

```powershell
conda create -n slmpy-browser python=3.11 -y
conda activate slmpy-browser
git clone https://github.com/mffg1993/SLMPy.git
cd SLMPy
git switch feature/browser-gpu-ui
python -m pip install -e ".[display,test]"
```

If you have a supported NVIDIA GPU and a compatible CUDA runtime/driver, install *one* CuPy variant. For CUDA 12:

```powershell
python -m pip install "cupy-cuda12x>=13"
```

For CUDA 13 use `cupy-cuda13x` instead. Do not install both variants together. CPU mode works without CuPy.

## Run

```powershell
python -m slmpy_browser
```

Open **http://127.0.0.1:8765** on the **same computer** if it does not open automatically.

The browser offers:

1. **Hologram Studio:** LG/HG phase-only patterns, blazed gratings, optional CPU/GPU calculation, grayscale preview, and FFT intensity estimate.
2. **Displays & Screens:** discover local monitors, select their *native reported resolution*, open a full-screen Qt output and update each screen independently; use Escape to close an output window.
3. **GPU Acceleration:** detect CUDA and CuPy, select CPU/GPU/auto, and benchmark warm CPU and GPU phase-generation-plus-FFT times. Benchmark excludes GPU-to-host copies, network/browser rendering, monitor refresh, and optical response.

The browser talks to FastAPI on localhost; independent Qt subprocesses drive fullscreen outputs. The app cannot drive SLMs connected to another workstation through this interface, and server/network exposure is intentionally disabled.

## Tests

```powershell
python -m pytest -q
```

Tests are hardware-free and exercise basic numerical invariants, preview generation, and local web endpoints. An actual Windows multi-monitor/hardware verification is still required.

## Known limitations and safety

**Not yet a validated SLM driver.** This is a research prototype, not a 1.1 replacement for the original code. It currently generates *phase-only* LG/HG/grating patterns rather than the complex-amplitude hologram encoding in your earlier scripts. The generated pattern is mapped linearly to 8-bit grayscale, which is **not** an appropriate substitute for measured wavelength- and device-specific phase-LUT calibration.

- The browser preview may be resized; the native Qt process rejects nonmatching frame dimensions. OS-level DPI scaling, monitor placement, grayscale/channel interpretation, and exact device pixel mapping must be checked experimentally.
- No hardware trigger, VSync barrier, or guaranteed synchronization between screens.
- The backend does not presently support amplitude masks, arbitrary complex-field encoding, Zernike correction, or physical beam propagation. These are future integrations of the original SLMPy physics, after their numerical issues have been resolved.
- GPU speedup is device-, shape-, and FFT-dependent. For small patterns, CPU can be faster. GPU output is copied back to system memory for display.
- Use a normal monitor before connecting a research SLM. Always follow your laser safety procedures.
- Close the application to shut down the managed native output processes.

## Architecture

```text
slmpy_browser/
  core.py                # NumPy/CuPy pattern computation, FFT, benchmark
  server.py              # FastAPI endpoints; local-only access
  display_worker.py      # one native Qt event loop per screen
  static/index.html      # tabbed browser control panel
  __main__.py            # localhost launcher
tests/
  test_browser_core.py
```

The original SLMpy GUI and scripting code remain in `Versions/`. The new prototype is deliberately isolated until numerical correctness and hardware performance are confirmed.

## Next development steps

- Device profile with wavelength-specific LUTs, calibration metadata and physical pixel geometry.
- Unit-test scientifically correct complex-amplitude hologram encoding and Fresnel propagation.
- Validate native full-screen pixel identity on Windows, including mixed DPI.
- Add scripted control, saved presets, optional camera feedback, and cross-monitor timing instrumentation.
