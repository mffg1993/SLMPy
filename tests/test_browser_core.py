"""Hardware-free scientific and API smoke tests."""
import numpy as np
import pytest
from fastapi.testclient import TestClient
from slmpy_browser.core import Settings, calculate_phase, generate, benchmark, validate
from slmpy_browser.server import app


def test_modes_are_finite_and_correct_shape():
    for mode in ("LG", "HG", "grating"):
        a = calculate_phase(Settings(width=128, height=96, mode=mode, p=2, n=2), np)
        assert a.shape == (96, 128)
        assert np.isfinite(a).all()
        assert a.min() >= 0
        assert a.max() < 2 * np.pi + 1e-5


def test_lg_changes_azimuthal_phase():
    a = calculate_phase(Settings(width=128, height=96, l=0), np)
    b = calculate_phase(Settings(width=128, height=96, l=2), np)
    assert not np.allclose(a, b)


def test_hg_orders_change_pattern():
    a = calculate_phase(Settings(width=128, height=96, mode="HG", m=0, n=0), np)
    b = calculate_phase(Settings(width=128, height=96, mode="HG", m=1, n=1), np)
    assert not np.allclose(a, b)


def test_grating_periodicity():
    a = calculate_phase(Settings(width=128, height=96, mode="grating", period_px=16), np)
    assert np.allclose(np.exp(1j*a[:,0]), np.exp(1j*a[:,16]), atol=1e-5)


def test_invalid_requests():
    with pytest.raises(ValueError):
        validate(Settings(width=10))
    with pytest.raises(ValueError):
        validate(Settings(backend="nonexistent"))


def test_cpu_generate():
    r = generate(Settings(width=128, height=96, backend="cpu"))
    assert r["image"].shape == (96, 128)
    assert r["image"].dtype == np.uint8
    assert r["preview"].startswith("data:image/png;base64,")
    assert r["fft_preview"].startswith("data:image/png;base64,")
    assert r["backend"] == "cpu"


def test_cpu_benchmark():
    r = benchmark(128, 96, 2)
    assert r["cpu"] >= 0


def test_preview_endpoint():
    with TestClient(app, base_url="http://127.0.0.1:8765") as client:
        r = client.post("/api/preview", json={"width": 128, "height": 96, "backend": "cpu"})
        assert r.status_code == 200, r.text
        assert r.json()["backend"] == "cpu"
        r = client.post("/api/preview", json={"width": 10})
        assert r.status_code == 422


def test_home_endpoint():
    with TestClient(app, base_url="http://127.0.0.1:8765") as client:
        r = client.get("/")
        assert r.status_code == 200
        assert "GPU Acceleration" in r.text
