"""
TEST SUITE: US2 – Translate Video
DESCRIPTION:
Automated tests for the /video/translate endpoint that handles ASL video uploads,
MediaPipe frame extraction, Roboflow inference, and JSON response generation.

Requirements: R2, R4, R5, R6
"""

import io
import os
import pytest
import numpy as np
import cv2
from fastapi.testclient import TestClient
from app import app  # FastAPI instance

client = TestClient(app)

# ------------------------------------------------------------------------
# Path setup: ensure test video directory exists
# ------------------------------------------------------------------------
TEST_VIDEO_DIR = os.path.join(os.path.dirname(__file__), "test_data")

def load_test_video(filename):
    """Loads an actual ASL test video from tests/test_data/. Skips test if missing."""
    path = os.path.join(TEST_VIDEO_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"Missing required test video: {filename}")
    return open(path, "rb")


# ===========================================================
# Helper: Tolerant sequence comparison
# ===========================================================
def tolerant_sequence_match(expected, actual):
    """Helper: allows partial or full sequence match for short videos."""
    if not actual:
        return False
    return expected.startswith(actual) or actual.startswith(expected[:len(actual)])


# ===========================================================
# TC-US2-01: Verify system accepts a valid ASL video
# ===========================================================
def test_translate_video_valid(monkeypatch):
    import routers.translate_video as translate_video

    sequence = iter(["A", "L", "Y"])
    monkeypatch.setattr(
        translate_video,
        "crop_hand_from_frame",
        lambda frame, hands: np.zeros((224, 224, 3), dtype=np.uint8)
    )
    monkeypatch.setattr(
        translate_video,
        "run_asl_inference",
        lambda image: {"label": next(sequence, "Y"), "confidence": 0.95}
    )

    with load_test_video("ASL_Short_Video.mp4") as f:
        response = client.post("/video/translate", files={"file": ("ASL_Short_Video.mp4", f, "video/mp4")})

    assert response.status_code == 200
    data = response.json()
    labels = [p["prediction"]["label"] for p in data["predictions"]]
    actual = "".join(labels)
    expected = "ALY"
    print(f"\nDEBUG: Expected {expected}, got {actual}")
    assert tolerant_sequence_match(expected, actual), f"Expected sequence '{expected}', got '{actual}'"


# ===========================================================
# TC-US2-02: Verify system rejects unsupported video formats
# ===========================================================
def test_translate_video_invalid_type():
    fake_file = io.BytesIO(b"fake content")
    response = client.post(
        "/video/translate",
        files={"file": ("invalid_file.docx", fake_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 400
    assert "Invalid" in response.text or "valid video" in response.text


# ===========================================================
# TC-US2-03: Verify MediaPipe preprocessing occurs
# ===========================================================
def test_translate_video_preprocessing(monkeypatch):
    import routers.translate_video as translate_video
    called_flags = {"preprocess": False}

    def mock_crop_hand_from_frame(frame, hands):
        called_flags["preprocess"] = True
        return np.zeros((224, 224, 3), dtype=np.uint8)

    def mock_run_asl_inference(image):
        assert image.shape == (224, 224, 3)
        return {"label": "A", "confidence": 0.95}

    monkeypatch.setattr(translate_video, "crop_hand_from_frame", mock_crop_hand_from_frame)
    monkeypatch.setattr(translate_video, "run_asl_inference", mock_run_asl_inference)

    with load_test_video("ASL_Short_Video.mp4") as f:
        response = client.post("/video/translate", files={"file": ("ASL_Short_Video.mp4", f, "video/mp4")})

    assert response.status_code == 200
    assert called_flags["preprocess"], "Preprocessing (crop_hand_from_frame) was not called."


# ===========================================================
# TC-US2-04: Verify concatenated sequence output
# ===========================================================
def test_translate_video_sequence(monkeypatch):
    import routers.translate_video as translate_video

    labels = ["O", "V", "F"]
    def mock_run_asl_inference(image):
        return {"label": labels.pop(0) if labels else "F", "confidence": 0.9}

    monkeypatch.setattr(
        translate_video,
        "crop_hand_from_frame",
        lambda frame, hands: np.zeros((224, 224, 3), dtype=np.uint8)
    )
    monkeypatch.setattr(
        translate_video,
        "run_asl_inference",
        mock_run_asl_inference
    )

    with load_test_video("ASL_Video_OVF.mp4") as f:
        response = client.post("/video/translate", files={"file": ("ASL_Video_OVF.mp4", f, "video/mp4")})

    assert response.status_code == 200
    data = response.json()
    output = "".join([p["prediction"]["label"] for p in data["predictions"]])
    assert output.startswith("OVF")
    assert all(p["prediction"]["confidence"] >= 0.8 for p in data["predictions"])


# ===========================================================
# TC-US2-05: Verify system handles long video gracefully
# ===========================================================
def test_translate_video_long(monkeypatch, tmp_path):
    video_path = tmp_path / "ASL_Long_Video.mp4"
    out = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*"mp4v"), 10, (64, 64))
    for _ in range(300):
        frame = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        out.write(frame)
    out.release()

    import routers.translate_video as translate_video
    monkeypatch.setattr(
        translate_video,
        "crop_hand_from_frame",
        lambda frame, hands: np.zeros((224, 224, 3), dtype=np.uint8)
    )
    monkeypatch.setattr(
        translate_video,
        "run_asl_inference",
        lambda image: {"label": "L", "confidence": 0.9}
    )

    with open(video_path, "rb") as f:
        response = client.post("/video/translate", files={"file": ("ASL_Long_Video.mp4", f, "video/mp4")})

    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) > 0


# ===========================================================
# TC-US2-06: Verify system displays error for corrupted video
# ===========================================================
def test_translate_video_corrupted(tmp_path):
    corrupted_path = tmp_path / "Corrupted_Video.mp4"
    with open(corrupted_path, "wb") as f:
        f.write(b"not a valid video file")

    with open(corrupted_path, "rb") as f:
        response = client.post("/video/translate", files={"file": ("Corrupted_Video.mp4", f, "video/mp4")})

    assert response.status_code in [400, 500]
    assert (
        "Unable to process" in response.text
        or "failed to open video file" in response.text.lower()
        or "error" in response.text.lower()
    )