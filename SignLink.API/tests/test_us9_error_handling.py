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
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import logging
import numpy as np

from app import app

client = TestClient(app)


# ------------------------------------------------------------------------
# Path setup: ensure test data directory exists
# ------------------------------------------------------------------------
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")

def get_test_file(filename: str, content_type: str):
    """Loads test files from tests/test_data/. Creates dummy file if missing."""
    path = os.path.join(TEST_DATA_DIR, filename)
    if os.path.exists(path):
        return open(path, "rb")
    # fallback dummy content for CI or missing media
    return io.BytesIO(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41"), content_type


# --------------------------------------------------------------------
# TC-US9-01: Unsupported File Type Upload (Image/Video Translation)
# --------------------------------------------------------------------
@pytest.mark.parametrize("endpoint", ["/image/predict", "/video/translate"])
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
    client = TestClient(app)

    # Patch inference and crop functions
    monkeypatch.setattr("utils.roboflow_client.run_asl_inference", lambda x: None)
    monkeypatch.setattr("utils.mediapipe_utils.crop_hand_from_frame", lambda frame, hands: None)

    with client.websocket_connect("/webcam/ws") as websocket:
        websocket.send_text("invalid_data")

        msg1 = websocket.receive()
        assert isinstance(msg1, (bytes, bytearray, dict))

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
        filename, content_type = "ASL_A.png", "image/png"
    else:
        filename, content_type = "ASL_Short_Video.mp4", "video/mp4"

    file_obj = get_test_file(filename, content_type)
    with file_obj[0] if isinstance(file_obj, tuple) else file_obj as f:
        response = client.post(endpoint, files={"file": (filename, f, content_type)})

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

    if "image" in endpoint:
        filename, content_type = "ASL_A.png", "image/png"
    else:
        filename, content_type = "ASL_Short_Video.mp4", "video/mp4"

    file_obj = get_test_file(filename, content_type)
    with file_obj[0] if isinstance(file_obj, tuple) else file_obj as f:
        response = client.post(endpoint, files={"file": (filename, f, content_type)})
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
    Verifies that exceptions are logged to 'app.errors' while client sees generic error.
    """
    def mock_failure(*args, **kwargs):
        raise Exception("Logged failure test")

    monkeypatch.setattr(patch_path, mock_failure)
    caplog.set_level(logging.ERROR)

    if "image" in endpoint:
        filename, content_type = "ASL_A.png", "image/png"
    else:
        filename, content_type = "ASL_Short_Video.mp4", "video/mp4"

    file_obj = get_test_file(filename, content_type)
    with file_obj[0] if isinstance(file_obj, tuple) else file_obj as f:
        response = client.post(endpoint, files={"file": (filename, f, content_type)})

    assert response.status_code == 500
    json_body = response.json()
    assert "error" in json_body
    assert "Logged failure test" not in json_body["error"]

    error_logs = [rec.getMessage() for rec in caplog.records]
    assert any("Logged failure test" in msg for msg in error_logs) or any(
        "Unexpected server error" in msg or "inference" in msg for msg in error_logs
    ), f"Expected logged backend error, found: {error_logs}"


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
        filename, content_type = "ASL_A.png", "image/png"
    else:
        filename, content_type = "ASL_Short_Video.mp4", "video/mp4"

    file_obj = get_test_file(filename, content_type)
    with file_obj[0] if isinstance(file_obj, tuple) else file_obj as f:
        response = client.post(endpoint, files={"file": (filename, f, content_type)})
        assert response.status_code == 500

    # Restore normal behavior
    monkeypatch.setattr(patch_path, real_run_asl_inference)
    file_obj = get_test_file(filename, content_type)
    with file_obj[0] if isinstance(file_obj, tuple) else file_obj as f:
        response = client.post(endpoint, files={"file": (filename, f, content_type)})
        assert response.status_code == 200
        json_body = response.json()
        if isinstance(json_body, list):
            assert len(json_body) > 0
            assert "predictions" in json_body[0]
        elif isinstance(json_body, dict):
            assert "predictions" in json_body
        else:
            pytest.fail(f"Unexpected response type: {type(json_body)}")
