"""Local-only FastAPI service for the SLMPy browser prototype.

Start with: python -m slmpy_browser
The server serves the UI; a separate Qt process handles each SLM display.
No public-network binding and no remote instrument control are supported.
"""
from __future__ import annotations

from dataclasses import asdict
from contextlib import asynccontextmanager
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ValidationError
from PIL import Image
from .core import Settings, benchmark, generate, gpu_info, validate


class PatternRequest(BaseModel):
    width: int = Field(default=1024, ge=64, le=2560)
    height: int = Field(default=768, ge=64, le=1600)
    mode: str = "LG"
    l: int = 1
    p: int = 0
    m: int = 0
    n: int = 0
    waist: float = 0.35
    period_px: float = 32.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    backend: str = "auto"

    def settings(self) -> Settings:
        s = Settings(**self.model_dump())
        validate(s)
        return s


class DisplayRequest(PatternRequest):
    screen: int = Field(ge=0)


class CloseRequest(BaseModel):
    screen: int = Field(ge=0)


class BenchmarkRequest(BaseModel):
    width: int = Field(default=1024, ge=64, le=2560)
    height: int = Field(default=768, ge=64, le=1600)
    repetitions: int = Field(default=5, ge=2, le=20)


_lock = threading.RLock()
_display_processes: dict[int, subprocess.Popen] = {}
_display_dir = tempfile.TemporaryDirectory(prefix="slmpy-display-")
_static = Path(__file__).parent / "static"


def _screen_info() -> list[dict]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "slmpy_browser.display_worker", "--list"],
            capture_output=True, text=True, timeout=8, check=True,
        )
        return json.loads(result.stdout.strip())
    except (FileNotFoundError, subprocess.SubprocessError, ValueError) as exc:
        raise RuntimeError(
            "Native display enumeration unavailable. Install PySide6 and "
            "run the application in a desktop session: " + str(exc)
        ) from exc


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    with _lock:
        for proc in _display_processes.values():
            if proc.poll() is None:
                proc.terminate()
        _display_processes.clear()
    _display_dir.cleanup()


app = FastAPI(title="SLMPy Browser", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def local_host_only(request: Request, call_next):
    # Prevent arbitrary DNS rebinding / nonlocal host aliases. Run Uvicorn
    # on 127.0.0.1 only. Requests are intentionally not CORS-enabled.
    from fastapi.responses import JSONResponse
    host = request.headers.get("host", "").split(":")[0].lower()
    if host not in ("127.0.0.1", "localhost"):
        return JSONResponse(status_code=403, content={"detail": "Local access only."})
    origin = request.headers.get("origin")
    if origin and origin.rstrip("/") not in ("http://127.0.0.1:%s" % request.url.port, "http://localhost:%s" % request.url.port):
        return JSONResponse(status_code=403, content={"detail": "Untrusted origin."})
    return await call_next(request)


@app.get("/")
def index():
    return FileResponse(_static / "index.html")


@app.get("/api/status")
def status():
    try:
        screens = _screen_info()
        screen_error = None
    except RuntimeError as exc:
        screens = []
        screen_error = str(exc)
    with _lock:
        active = [idx for idx, proc in _display_processes.items() if proc.poll() is None]
    return {"gpu": gpu_info(), "screens": screens, "screen_error": screen_error,
            "active_screens": active, "warning": "Preview is not an SLM phase calibration."}


@app.post("/api/preview")
def preview(request: PatternRequest):
    try:
        result = generate(request.settings())
    except (ValueError, RuntimeError, MemoryError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {k: v for k, v in result.items() if k != "image"}


@app.post("/api/benchmark")
def benchmark_api(request: BenchmarkRequest):
    try:
        return benchmark(request.width, request.height, request.repetitions)
    except (ValueError, RuntimeError, MemoryError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/display")
def display(request: DisplayRequest):
    try:
        screens = _screen_info()
        if request.screen >= len(screens):
            raise ValueError("Selected screen is no longer available.")
        target = screens[request.screen]
        s = PatternRequest(**request.model_dump(exclude={"screen"})).settings()
        if (s.width, s.height) != (target["width"], target["height"]):
            raise ValueError(
                "Use the native resolution for screen %d: %dx%d." %
                (request.screen, target["width"], target["height"])
            )
        result = generate(s, with_fft=False)
        buffer = BytesIO()
        Image.fromarray(result["image"], mode="L").save(buffer, format="PNG")
        with _lock:
            image_path = Path(_display_dir.name) / ("screen_%d.png" % request.screen)
            temp_path = image_path.with_suffix(".new")
            temp_path.write_bytes(buffer.getvalue())
            os.replace(temp_path, image_path)
            proc = _display_processes.get(request.screen)
            if proc is None or proc.poll() is not None:
                proc = subprocess.Popen(
                    [sys.executable, "-m", "slmpy_browser.display_worker",
                     "--screen", str(request.screen), "--image", str(image_path)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                _display_processes[request.screen] = proc
        return {"ok": True, "screen": request.screen, "backend": result["backend"],
                "compute_ms": result["compute_ms"],
                "warning": "Uncalibrated grayscale output; verify on a safe test monitor first."}
    except (ValueError, RuntimeError, MemoryError, OSError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/close")
def close_display(request: CloseRequest):
    with _lock:
        proc = _display_processes.pop(request.screen, None)
        if proc and proc.poll() is None:
            proc.terminate()
    return {"ok": True, "screen": request.screen}
