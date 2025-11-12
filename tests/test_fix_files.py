from pathlib import Path

from starlette.testclient import TestClient

from src.app import app
from src.security.files import JPEG_EOI, JPEG_SOI, PNG


def test_upload_rejects_bad_type(tmp_path: Path):
    c = TestClient(app)
    data = b"not_image"
    files = {"file": ("x.bin", data, "application/octet-stream")}
    r = c.post("/events/1/image", files=files)
    assert r.status_code == 422
    assert "bad_type" in r.text


def test_upload_accepts_png(tmp_path: Path):
    c = TestClient(app)
    data = PNG + b"abc"
    files = {"file": ("x.png", data, "image/png")}
    r = c.post("/events/1/image", files=files)
    assert r.status_code == 200
    assert Path(r.json()["path"]).exists()


def test_upload_accepts_jpeg(tmp_path: Path):
    c = TestClient(app)
    data = JPEG_SOI + b"abc" + JPEG_EOI
    files = {"file": ("x.jpg", data, "image/jpeg")}
    r = c.post("/events/1/image", files=files)
    assert r.status_code == 200
