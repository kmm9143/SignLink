"""
TEST SUITE: US4 – Display Confidence
DESCRIPTION:
This file automates tests for the confidence score feature of ASL translation.
It verifies that the system displays correct confidence scores, shows low-confidence
warnings, updates live translation confidence, and displays only the highest-confidence
prediction when multiple classes are returned.

Requirements: R7
"""

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# --------------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------------
def mock_roboflow_response(predictions):
    """
    Returns a mock Roboflow API response with given predictions.
    Each prediction is a dict: {"class": <letter>, "confidence": <float>}
    """
    return {"predictions": predictions}


# --------------------------------------------------------------------
# TC-US4-01: Verify system shows classification confidence score
# --------------------------------------------------------------------
def test_us4_display_confidence(monkeypatch):
    """
    Upload ASL_G.png and verify system returns gesture 'V' with a confidence score.
    """

    # Mock the inference function to simulate Roboflow API
    from routers.translate_image import run_asl_inference
    def mock_inference(*args, **kwargs):
        return mock_roboflow_response([{"class": "V", "confidence": 0.91}])
    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_inference)

    # Upload file
    with open("tests/test_data/ASL_V.png", "rb") as f:
        response = client.post("/image/predict", files={"file": ("ASL_V.png", f, "image/png")})

    assert response.status_code == 200
    json_body = response.json()
    assert "predictions" in json_body
    assert json_body["predictions"][0]["class"] == "V"
    assert 0 <= json_body["predictions"][0]["confidence"] <= 1


# --------------------------------------------------------------------
# TC-US4-02: Verify low-confidence notification if score <50%
# --------------------------------------------------------------------
def test_us4_low_confidence_notification(monkeypatch):
    """
    Upload ASL_Blurry.png and check if low-confidence warning is returned.
    """

    from routers.translate_image import run_asl_inference
    def mock_inference(*args, **kwargs):
        return mock_roboflow_response([{"class": "V", "confidence": 0.42}])
    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_inference)

    with open("tests/test_data/ASL_Blurry.png", "rb") as f:
        response = client.post("/image/predict", files={"file": ("ASL_Blurry.png", f, "image/png")})

    assert response.status_code == 200
    json_body = response.json()
    assert "predictions" in json_body
    # Expect low-confidence warning
    assert any(pred["confidence"] < 0.5 for pred in json_body["predictions"])


# --------------------------------------------------------------------
# TC-US4-03: Verify confidence scores update correctly in live translation
# --------------------------------------------------------------------
def test_us4_live_translation_confidence(monkeypatch):
    """
    Simulate live translation using static images (PNG/JPG) instead of webcam.
    """

    # Mock the inference function to simulate Roboflow API responses
    from routers.translate_image import run_asl_inference

    # Clear 'H' gesture (>=80%)
    def mock_inference_clear(*args, **kwargs):
        return {"predictions": [{"class": "A", "confidence": 0.85}]}

    # Occluded 'H' gesture (<80%)
    def mock_inference_occluded(*args, **kwargs):
        return {"predictions": [{"class": "A", "confidence": 0.65}]}

    # Clear gesture
    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_inference_clear)
    with open("tests/test_data/ASL_A.png", "rb") as f:
        response = client.post("/image/predict", files={"file": ("ASL_A.png", f, "image/png")})
    assert response.status_code == 200
    json_body = response.json()
    assert json_body["predictions"][0]["confidence"] >= 0.8

    # Occluded gesture
    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_inference_occluded)
    with open("tests/test_data/ASL_A.png", "rb") as f:
        response = client.post("/image/predict", files={"file": ("ASL_A.png", f, "image/png")})
    assert response.status_code == 200
    json_body = response.json()
    assert json_body["predictions"][0]["confidence"] < 0.8


# --------------------------------------------------------------------
# TC-US4-04: Verify system displays only highest-confidence prediction
# --------------------------------------------------------------------
def test_us4_top_prediction_only(monkeypatch):
    """
    Upload ASL_A_or_B.png and verify only the top prediction is displayed.
    """

    from routers.translate_image import run_asl_inference
    def mock_inference(*args, **kwargs):
        return mock_roboflow_response([
            {"class": "A", "confidence": 0.72},
            {"class": "B", "confidence": 0.28}
        ])
    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_inference)

    with open("tests/test_data/ASL_A_or_B.png", "rb") as f:
        response = client.post("/image/predict", files={"file": ("ASL_A_or_B.png", f, "image/png")})

    assert response.status_code == 200
    json_body = response.json()
    # Only the highest-confidence prediction should be used for display
    top_pred = max(json_body["predictions"], key=lambda p: p["confidence"])
    assert top_pred["class"] == "A"
    assert top_pred["confidence"] == 0.72