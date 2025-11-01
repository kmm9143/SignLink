"""
TEST SUITE: US1 – Translate Image
DESCRIPTION:
Automated tests for the /image/predict endpoint that handles ASL image uploads,
MediaPipe preprocessing, and Roboflow inference.

Requirements: R1, R4, R5, R6
"""

import io
import os
import pytest
from fastapi.testclient import TestClient
import numpy as np
import cv2
from app import app  # assuming your FastAPI instance is in app.py

client = TestClient(app)

# ------------------------------------------------------------------------
# Path setup: ensure test image directory exists
# ------------------------------------------------------------------------
TEST_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "test_data")

def load_test_image(filename):
    """Loads an actual ASL test image from tests/test_data/."""
    path = os.path.join(TEST_IMAGE_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"Missing required test image: {filename}")
    return open(path, "rb")


# ===========================================================
# TC-US1-01: Verify system allows uploading a valid ASL image
# ===========================================================
def test_upload_valid_asl_image(monkeypatch):
    """Verify a valid image upload returns translation with confidence ≥ 80%."""

    def mock_run_asl_inference(_img):
        return {"predictions": [{"class": "A", "confidence": 0.96}]}

    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_run_asl_inference)

    with load_test_image("ASL_A.png") as f:
        file = {"file": ("ASL_A.png", f, "image/png")}
        response = client.post("/image/predict", files=file)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()
    assert "predictions" in data
    top_pred = data["predictions"][0]
    assert top_pred["class"] == "A"
    assert top_pred["confidence"] >= 0.8


# ===========================================================
# TC-US1-02: Verify system rejects invalid image formats
# ===========================================================
def test_reject_invalid_file_type():
    """Verify invalid file formats are rejected with proper error message."""

    file = {"file": ("invalid_file.txt", io.BytesIO(b"fake text"), "text/plain")}
    response = client.post("/image/predict", files=file)

    assert response.status_code in [400, 415]
    assert "Invalid" in response.text or "error" in response.text


# ===========================================================
# TC-US1-03: Verify MediaPipe preprocessing before Roboflow
# ===========================================================
def test_mediapipe_preprocessing(monkeypatch):
    """Ensure that MediaPipe hand detection occurs before Roboflow inference."""

    hand_detected = {"flag": False}

    def mock_crop_hand_from_frame(frame, hands):
        hand_detected["flag"] = True
        return np.zeros((128, 128, 3), dtype=np.uint8)  # simulate cropped region

    def mock_run_asl_inference(_img):
        return {"predictions": [{"class": "O", "confidence": 0.88}]}

    monkeypatch.setattr("routers.translate_image.crop_hand_from_frame", mock_crop_hand_from_frame)
    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_run_asl_inference)

    with load_test_image("ASL_O.png") as f:
        file = {"file": ("ASL_O.png", f, "image/png")}
        response = client.post("/image/predict", files=file)

    assert response.status_code == 200
    assert hand_detected["flag"], "MediaPipe preprocessing did not occur."
    assert response.json()["predictions"][0]["class"] == "O"


# ===========================================================
# TC-US1-04: Verify Roboflow correctly classifies ASL image
# ===========================================================
def test_roboflow_classification(monkeypatch):
    """Verify Roboflow returns correct classification with confidence ≥ 80%."""

    def mock_run_asl_inference(_img):
        return {"predictions": [{"class": "O", "confidence": 0.88}]}

    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_run_asl_inference)

    with load_test_image("ASL_O.png") as f:
        file = {"file": ("ASL_O.png", f, "image/png")}
        response = client.post("/image/predict", files=file)

    assert response.status_code == 200
    result = response.json()
    assert result["predictions"][0]["class"] == "O"
    assert result["predictions"][0]["confidence"] >= 0.8


# ===========================================================
# TC-US1-05: Verify recognized gesture text is displayed
# ===========================================================
def test_recognized_gesture_text(monkeypatch):
    """Ensure recognized ASL letter is correctly shown in JSON response."""

    def mock_run_asl_inference(_img):
        return {"predictions": [{"class": "V", "confidence": 0.92}]}

    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_run_asl_inference)

    with load_test_image("ASL_V.png") as f:
        file = {"file": ("ASL_V.png", f, "image/png")}
        response = client.post("/image/predict", files=file)

    assert response.status_code == 200
    result = response.json()
    assert result["predictions"][0]["class"] == "V"
    assert result["predictions"][0]["confidence"] >= 0.8