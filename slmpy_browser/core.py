"""Computational core for SLMPy Browser. No Qt dependencies.

GPU computation is optional and uses CuPy when explicitly selected or when
auto-selection detects a working CUDA device.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from io import BytesIO
import base64
import time

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class Settings:
    width: int = 1024
    height: int = 768
    mode: str = "LG"                   # LG, HG, or grating
    l: int = 1
    p: int = 0
    m: int = 0
    n: int = 0
    waist: float = 0.35              # relative to half-width
    period_px: float = 32.0
    offset_x: float = 0.0            # normalized half-width coordinates
    offset_y: float = 0.0
    backend: str = "auto"             # auto, cpu, gpu


def validate(s: Settings) -> None:
    if not (64 <= s.width <= 2560 and 64 <= s.height <= 1600):
        raise ValueError("Resolution must be between 64x64 and 2560x1600.")
    if s.width * s.height > 3_200_000:
        raise ValueError("Maximum image size is 3.2 million pixels.")
    if s.mode not in ("LG", "HG", "grating"):
        raise ValueError("Unknown hologram mode.")
    if not (-30 <= s.l <= 30 and 0 <= s.p <= 20 and 0 <= s.m <= 30 and 0 <= s.n <= 30):
        raise ValueError("Mode indices out of range.")
    if not (0.01 <= s.waist <= 2):
        raise ValueError("Waist must lie between 0.01 and 2.")
    if not (2 <= s.period_px <= 2048):
        raise ValueError("Grating period must be between 2 and 2048 pixels.")
    if abs(s.offset_x) > 1 or abs(s.offset_y) > 1:
        raise ValueError("Normalized offsets must lie between -1 and 1.")
    if s.backend not in ("cpu", "gpu", "auto"):
        raise ValueError("Unknown backend.")


def gpu_info() -> dict:
    """Report a usable CUDA device, without requiring CuPy for CPU-only usage."""
    try:
        import cupy as cp
        count = int(cp.cuda.runtime.getDeviceCount())
        if not count:
            return {"available": False, "reason": "No CUDA devices detected."}
        prop = cp.cuda.runtime.getDeviceProperties(0)
        raw_name = prop.get("name", b"CUDA GPU")
        name = raw_name.decode(errors="replace") if isinstance(raw_name, bytes) else str(raw_name)
        free, total = cp.cuda.runtime.memGetInfo()
        return {
            "available": True,
            "device": name,
            "devices": count,
            "memory_gb": round(total / 1024 ** 3, 2),
            "free_gb": round(free / 1024 ** 3, 2),
            "cupy": cp.__version__,
        }
    except Exception as exc:
        return {"available": False, "reason": "%s: %s" % (type(exc).__name__, exc)}


def choose_backend(choice: str):
    if choice == "cpu":
        return np, "cpu"
    info = gpu_info()
    if info["available"]:
        import cupy as cp
        return cp, "gpu"
    if choice == "gpu":
        raise RuntimeError("GPU requested but unavailable: " + info["reason"])
    return np, "cpu"


def _laguerre(p: int, alpha: int, z, xp):
    """Generalized Laguerre L_p^alpha, recurrence valid on NumPy and CuPy."""
    a = xp.ones_like(z)
    if p == 0:
        return a
    b = 1 + alpha - z
    for k in range(2, p + 1):
        a, b = b, ((2*k - 1 + alpha - z)*b - (k - 1 + alpha)*a) / k
    return b


def _hermite(order: int, z, xp):
    a = xp.ones_like(z)
    if order == 0:
        return a
    b = 2 * z
    for k in range(2, order + 1):
        a, b = b, 2*z*b - 2*(k-1)*a
    return b


def calculate_phase(s: Settings, xp):
    """Phase-only LG/HG mode with horizontal blazed grating, radians in [0,2π).

    Units of waist and offsets are normalized; phase-only encoding does not
    reproduce an arbitrary complex amplitude. Device calibration is separate.
    """
    x = xp.linspace(-1.0, 1.0, s.width, dtype=xp.float32) - s.offset_x
    y = xp.linspace(-1.0, 1.0, s.height, dtype=xp.float32) - s.offset_y
    xx, yy = xp.meshgrid(x, y)
    if s.mode == "LG":
        r2 = xx*xx + yy*yy
        rho = xp.sqrt(r2)
        field_phase = s.l * xp.arctan2(yy, xx)
        radial = _laguerre(s.p, abs(s.l), 2*r2/(s.waist*s.waist), xp)
        # Sign changes at radial nodes contribute pi to the field phase.
        field_phase = field_phase + xp.where(radial < 0, xp.pi, 0.0)
    elif s.mode == "HG":
        hx = _hermite(s.m, xp.sqrt(2.0)*xx/s.waist, xp)
        hy = _hermite(s.n, xp.sqrt(2.0)*yy/s.waist, xp)
        field_phase = xp.where(hx*hy < 0, xp.pi, 0.0)
    else:
        field_phase = xp.zeros_like(xx)
    px = xp.arange(s.width, dtype=xp.float32)[None, :]
    blaze = 2 * xp.pi * px / s.period_px
    return xp.mod(field_phase + blaze, 2*xp.pi).astype(xp.float32)


def sync(xp) -> None:
    if xp is not np:
        xp.cuda.Stream.null.synchronize()


def phase_to_uint8(phase, xp):
    """Uncalibrated linear phase -> 8-bit mapping. NOT a device LUT."""
    pixels = xp.floor(phase * (256.0 / (2 * xp.pi)))
    return xp.clip(pixels, 0, 255).astype(xp.uint8)


def to_cpu(a, xp):
    return a if xp is np else xp.asnumpy(a)


def image_data_uri(a: np.ndarray, max_width: int = 740) -> str:
    image = Image.fromarray(a, mode="L")
    if image.width > max_width:
        new_size = (max_width, max(1, round(image.height * max_width / image.width)))
        image = image.resize(new_size, resample=Image.Resampling.NEAREST)
    buf = BytesIO()
    image.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def generate(s: Settings, with_fft: bool = True) -> dict:
    validate(s)
    xp, used = choose_backend(s.backend)
    start = time.perf_counter()
    phase = calculate_phase(s, xp)
    if with_fft:
        # FFT of the phase-only pattern, not the original complex beam.
        stride = max(1, int(np.ceil(max(s.width, s.height) / 512)))
        small = phase[::stride, ::stride]
        intensity = xp.abs(xp.fft.fftshift(xp.fft.fft2(xp.exp(1j*small))))**2
        fft_log = xp.log1p(intensity)
        fft_log = fft_log / xp.maximum(xp.max(fft_log), 1e-12)
        spectrum = xp.clip(255*fft_log, 0, 255).astype(xp.uint8)
    else:
        spectrum = None
    gray = phase_to_uint8(phase, xp)
    sync(xp)
    compute_ms = 1000*(time.perf_counter() - start)
    start_transfer = time.perf_counter()
    image = np.ascontiguousarray(to_cpu(gray, xp))
    fft_image = to_cpu(spectrum, xp) if spectrum is not None else None
    transfer_ms = 1000*(time.perf_counter() - start_transfer)
    return {
        "image": image,
        "preview": image_data_uri(image),
        "fft_preview": image_data_uri(fft_image) if fft_image is not None else None,
        "backend": used,
        "compute_ms": round(compute_ms, 3),
        "transfer_ms": round(transfer_ms, 3),
        "dimensions": [s.width, s.height],
        "calibrated": False,
    }


def benchmark(width: int = 1024, height: int = 768, repetitions: int = 5) -> dict:
    if width * height > 3_200_000 or min(width, height) < 64:
        raise ValueError("Benchmark dimensions out of range.")
    if not 2 <= repetitions <= 20:
        raise ValueError("Repetitions must be between 2 and 20.")
    results = {}
    for requested in ("cpu", "gpu"):
        try:
            s = Settings(width=width, height=height, backend=requested)
            xp, used = choose_backend(requested)
            # Warm up kernels, FFT setup, and memory pools.
            for _ in range(2):
                phase = calculate_phase(s, xp)
                _ = xp.fft.fft2(xp.exp(1j*phase))
                sync(xp)
            times = []
            for _ in range(repetitions):
                start = time.perf_counter()
                phase = calculate_phase(s, xp)
                _ = xp.fft.fft2(xp.exp(1j*phase))
                sync(xp)
                times.append(1000*(time.perf_counter()-start))
            results[used] = round(float(np.median(times)), 3)
        except RuntimeError as exc:
            results[requested] = None
            results["gpu_note"] = str(exc)
    if results.get("gpu") is not None and results.get("cpu"):
        results["speedup"] = round(results["cpu"] / results["gpu"], 2)
    return {"width": width, "height": height, "repetitions": repetitions,
            "measurement": "median warm compute+FFT milliseconds, excludes transfer/display",
            **results}
