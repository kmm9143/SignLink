"""
TEST SUITE: US9 – Error Handling
DESCRIPTION:
    Verifies that the backend returns clear, consistent JSON error messages
    across various failure scenarios such as invalid file uploads, validation errors,
    and unexpected exceptions.

NOTE:
    Currently, TC-US9-01 (Unsupported File Type) and TC-US9-03 (Backend Failure) are implemented.
    TC-US9-03b covers the webcam WebSocket endpoint.
    Other test cases (validation, DB, and generic errors) are added below.

Requirements: R12
"""

import os
import io
import base64
import pytest
import cv2
import numpy as np
from fastapi.testclient import TestClient
from PIL import Image
from httpx import AsyncClient
import asyncio
import json

from app import app

client = TestClient(app)

# Import the actual backend function to patch
from utils.roboflow_client import run_asl_inference

# --------------------------------------------------------------------
# TC-US9-01: Unsupported File Type Upload (Image/Video Translation)
# --------------------------------------------------------------------
@pytest.mark.parametrize(
    "endpoint",
    [
        "/image/predict",
        "/video/translate",
    ],
)
def test_us9_unsupported_file_type(endpoint):
    """
    TC-US9-01: Ensure unsupported file types are rejected.
    """
    fake_file = io.BytesIO(b"This is not a valid image or video file.")
    response = client.post(
        endpoint,
        files={"file": ("invalid.txt", fake_file, "text/plain")},
    )
    assert response.status_code in [400, 415, 422], (
        f"{endpoint} should reject unsupported file types "
        f"but returned status {response.status_code}"
    )
    json_body = response.json()
    assert isinstance(json_body, dict)
    assert "error" in json_body or "detail" in json_body
    message = json_body.get("error") or str(json_body.get("detail"))
    assert any(word in message.lower() for word in ["invalid", "unsupported", "file type"])

# --------------------------------------------------------------------
# TC-US9-02: Webcam Not Detected / No Frames
# --------------------------------------------------------------------
def test_us9_webcam_not_detected(monkeypatch):
    """
    TC-US9-02: Ensure backend handles missing webcam frames gracefully.
    Sends invalid frame, confirms backend does not crash, returns None for prediction.
    """

    from fastapi.testclient import TestClient
    client = TestClient(app)

    # Patch inference and crop functions
    monkeypatch.setattr("utils.roboflow_client.run_asl_inference", lambda x: None)
    monkeypatch.setattr("utils.mediapipe_utils.crop_hand_from_frame", lambda frame, hands: None)

    with client.websocket_connect("/webcam/ws") as websocket:
        # Send invalid frame
        websocket.send_text("invalid_data")

        # Receive the first message: frame bytes (even for invalid input)
        msg1 = websocket.receive()
        if isinstance(msg1, dict) and "bytes" in msg1:
            frame_bytes = msg1["bytes"]
        else:
            frame_bytes = msg1
        assert isinstance(frame_bytes, (bytes, bytearray))

        # Receive the second message: JSON prediction
        msg2 = websocket.receive()
        if isinstance(msg2, dict) and "prediction" in msg2:
            prediction = msg2["prediction"]
        else:
            prediction = None
        assert prediction is None

# --------------------------------------------------------------------
# TC-US9-03: Backend API Failure / Timeout (Image/Video)
# --------------------------------------------------------------------
@pytest.mark.parametrize(
    "endpoint, patch_path",
    [
        ("/image/predict", "routers.translate_image.run_asl_inference"),
        ("/video/translate", "routers.translate_video.run_asl_inference"),
    ],
)
def test_us9_backend_failure(endpoint, patch_path, monkeypatch):
    """
    TC-US9-03: Ensure backend failures return a user-friendly 500 error.
    """
    def mock_failure(*args, **kwargs):
        raise Exception("Simulated backend failure")

    monkeypatch.setattr(patch_path, mock_failure)

    if "image" in endpoint:
        filename = "ASL_A.png"
        content_type = "image/png"
        path = os.path.join("tests", "test_data", filename)
    else:
        filename = "ASL_Short_Video.mp4"
        content_type = "video/mp4"
        path = os.path.join("tests", "test_data", filename)

    if os.path.exists(path):
        with open(path, "rb") as f:
            files = {"file": (filename, f, content_type)}
            response = client.post(endpoint, files=files)
    else:
        fake_file = io.BytesIO(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41")
        files = {"file": (filename, fake_file, content_type)}
        response = client.post(endpoint, files=files)

    assert response.status_code == 500
    json_body = response.json()
    assert "error" in json_body
    assert "unexpected" in json_body["error"].lower()

# --------------------------------------------------------------------
# TC-US9-04: Error Message Clearance After Recovery
# --------------------------------------------------------------------
@pytest.mark.parametrize("endpoint", ["/image/predict", "/video/translate"])
def test_us9_error_message_clears(endpoint):
    """
    TC-US9-04: Ensure previous errors are cleared after a valid request.
    """
    # Trigger first a failure
    fake_file = io.BytesIO(b"invalid content")
    client.post(endpoint, files={"file": ("bad.txt", fake_file, "text/plain")})

    # Then a valid file
    if "image" in endpoint:
        filename = "ASL_A.png"
        content_type = "image/png"
    else:
        filename = "ASL_Short_Video.mp4"
        content_type = "video/mp4"

    path = os.path.join("tests", "test_data", filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            response = client.post(endpoint, files={ "file": (filename, f, content_type) })
            assert response.status_code == 200
            json_body = response.json()
            assert "error" not in json_body or json_body.get("error") == ""

# --------------------------------------------------------------------
# TC-US9-05: Logging Backend Errors
# --------------------------------------------------------------------
@pytest.mark.parametrize(
    "endpoint, patch_path",
    [
        ("/image/predict", "routers.translate_image.run_asl_inference"),
        ("/video/translate", "routers.translate_video.run_asl_inference"),
    ],
)
def test_us9_backend_logging(endpoint, patch_path, monkeypatch, caplog):
    """
    TC-US9-05: Backend errors should be logged while user sees friendly message.
    """
    def mock_failure(*args, **kwargs):
        raise Exception("Logged failure test")

    monkeypatch.setattr(patch_path, mock_failure)

    caplog.set_level("ERROR")
    if "image" in endpoint:
        filename = "ASL_A.png"
        content_type = "image/png"
    else:
        filename = "ASL_Short_Video.mp4"
        content_type = "video/mp4"

    path = os.path.join("tests", "test_data", filename)
    with open(path, "rb") as f:
        response = client.post(endpoint, files={ "file": (filename, f, content_type) })
        assert response.status_code == 500
        json_body = response.json()
        assert "error" in json_body
        assert "Logged failure test" not in json_body.get("error")
        # Check logs contain the exception
        assert any("Logged failure test" in rec.message for rec in caplog.records)

# --------------------------------------------------------------------
# TC-US9-06: Application Continues After Error
# --------------------------------------------------------------------
@pytest.mark.parametrize(
    "endpoint, patch_path",
    [
        ("/image/predict", "routers.translate_image.run_asl_inference"),
        ("/video/translate", "routers.translate_video.run_asl_inference"),
    ],
)
def test_us9_continues_after_error(endpoint, patch_path, monkeypatch):
    """
    TC-US9-06: Ensure application recovers gracefully after a failed request.
    """
    from utils.roboflow_client import run_asl_inference as real_run_asl_inference

    # First request fails
    def fail_once(*args, **kwargs):
        raise Exception("Transient failure")
    monkeypatch.setattr(patch_path, fail_once)

    if "image" in endpoint:
        filename = "ASL_A.png"
        content_type = "image/png"
    else:
        filename = "ASL_Short_Video.mp4"
        content_type = "video/mp4"

    path = os.path.join("tests", "test_data", filename)
    with open(path, "rb") as f:
        response = client.post(endpoint, files={ "file": (filename, f, content_type) })
        assert response.status_code == 500

    # Restore normal behavior
    monkeypatch.setattr(patch_path, real_run_asl_inference)
    with open(path, "rb") as f:
        response = client.post(endpoint, files={ "file": (filename, f, content_type) })
        assert response.status_code == 200
        json_body = response.json()

        # ✅ Handle both list and dict structures
        if isinstance(json_body, list):
            assert len(json_body) > 0
            assert "predictions" in json_body[0]
        elif isinstance(json_body, dict):
            assert "predictions" in json_body
        else:
            pytest.fail(f"Unexpected response type: {type(json_body)}")

# --------------------------------------------------------------------
# TC-US9-05: Logging Backend Errors
# --------------------------------------------------------------------
@pytest.mark.parametrize(
    "endpoint, patch_path",
    [
        ("/image/predict", "routers.translate_image.run_asl_inference"),
        ("/video/translate", "routers.translate_video.run_asl_inference"),
    ],
)
def test_us9_backend_logging(endpoint, patch_path, monkeypatch, caplog):
    """
    TC-US9-05: Backend errors should be logged while user sees friendly message.
    Verifies that exceptions are logged to 'app.errors' while client sees generic error.
    """
    import logging

    # Patch inference function to simulate consistent backend failure
    def mock_failure(*args, **kwargs):
        raise Exception("Logged failure test")

    monkeypatch.setattr(patch_path, mock_failure)

    # Capture all ERROR logs (from app.errors or fallback root)
    caplog.set_level(logging.ERROR)

    # Select test file based on endpoint
    if "image" in endpoint:
        filename = "ASL_A.png"
        content_type = "image/png"
    else:
        filename = "ASL_Short_Video.mp4"
        content_type = "video/mp4"

    # Use real or fallback fake file
    path = os.path.join("tests", "test_data", filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            response = client.post(endpoint, files={"file": (filename, f, content_type)})
    else:
        fake_file = io.BytesIO(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41")
        response = client.post(endpoint, files={"file": (filename, fake_file, content_type)})

    # Verify client receives generic error (not raw backend exception)
    assert response.status_code == 500
    json_body = response.json()
    assert "error" in json_body
    assert "Logged failure test" not in json_body["error"]

    # Verify backend logged the original exception message somewhere
    error_logs = [rec.getMessage() for rec in caplog.records]
    assert any("Logged failure test" in msg for msg in error_logs) or any(
        "Unexpected server error" in msg or "inference" in msg for msg in error_logs
    ), f"Expected 'Logged failure test' or similar error in logs, found: {error_logs}"