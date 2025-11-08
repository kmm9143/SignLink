"""
TEST SUITE: US9 – Error Handling
DESCRIPTION:
    Verifies that the backend returns clear, consistent JSON error messages
    across various failure scenarios such as invalid file uploads, validation errors,
    and unexpected exceptions.

NOTE:
    Currently, TC-US9-01 (Unsupported File Type) and TC-US9-03 (Backend Failure) are implemented.
    TC-US9-03b covers the webcam WebSocket endpoint.
    Other test cases (validation, DB, and generic errors) can be added later.

Requirements: R12
"""

import os
import io
import base64
import pytest
import cv2
import numpy as np
from fastapi.testclient import TestClient
from PIL import Image  # For mock crop

# Async client for WebSocket testing
from httpx import AsyncClient
import asyncio
import json

from app import app  # Import the FastAPI instance

client = TestClient(app)

# Import the actual backend function to patch
from utils.roboflow_client import run_asl_inference


# --------------------------------------------------------------------
# TC-US9-01: Unsupported File Type Upload (Image/Video Translation)
# --------------------------------------------------------------------
@pytest.mark.parametrize(
    "endpoint",
    [
        "/image/predict",   # Image translation page
        "/video/translate", # Video translation page
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

    # Verify status code is one of expected client errors
    assert response.status_code in [400, 415, 422], (
        f"{endpoint} should reject unsupported file types "
        f"but returned status {response.status_code}"
    )

    # Confirm JSON response
    json_body = response.json()
    assert isinstance(json_body, dict), f"{endpoint} should return a JSON response."

    # Must contain a human-readable error key
    assert "error" in json_body or "detail" in json_body, (
        f"{endpoint} response missing 'error' or 'detail' field."
    )

    # Message clarity check
    message = json_body.get("error") or str(json_body.get("detail"))
    assert any(
        word in message.lower() for word in ["invalid", "unsupported", "file type"]
    ), f"{endpoint} returned unclear error message: {message}"


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

    # Select test file
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

    assert response.status_code == 500, f"{endpoint} should return 500, got {response.status_code}"
    json_body = response.json()
    assert "error" in json_body
    assert "unexpected" in json_body["error"].lower()
