"""
TEST SUITE: US2 – Translate Video
DESCRIPTION:
This file automates tests for the /video/translate endpoint that handles ASL video uploads,
MediaPipe frame extraction, Roboflow inference, and JSON response generation.

Requirements: R2, R4, R5, R6
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np
import cv2
import os

from app import app

client = TestClient(app)

# ----------------------------------------------------------------------
# FIXTURE: Simulate a small valid MP4 video file
# ----------------------------------------------------------------------
@pytest.fixture
def sample_video(tmp_path):
    """Creates a temporary valid MP4 video with random frames."""
    video_path = tmp_path / "temp_video.mp4"
    frame_height, frame_width = 64, 64
    out = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        10,  # 10 FPS
        (frame_width, frame_height)
    )

    for _ in range(10):
        frame = np.random.randint(0, 255, (frame_height, frame_width, 3), dtype=np.uint8)
        out.write(frame)

    out.release()
    return video_path


# ----------------------------------------------------------------------
# TEST CASE 1: Valid video upload
# ----------------------------------------------------------------------
def test_translate_video_valid(monkeypatch, sample_video):
    """Test uploading a valid MP4 video returns predictions."""

    import routers.translate_video as translate_video

    # Mock the actual functions *used* inside the router
    monkeypatch.setattr(translate_video, "crop_hand_from_frame", lambda frame, hands: np.zeros((224, 224, 3), dtype=np.uint8))
    monkeypatch.setattr(translate_video, "run_asl_inference", lambda image: {"label": "A", "confidence": 0.95})

    with open(sample_video, "rb") as f:
        response = client.post(
            "/video/translate",
            files={"file": ("temp_video.mp4", f, "video/mp4")}
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) > 0
    assert data["predictions"][0]["prediction"]["label"] == "A"


# ----------------------------------------------------------------------
# TEST CASE 2: Invalid file type
# ----------------------------------------------------------------------
def test_translate_video_invalid_type():
    """Test rejection of unsupported file types."""
    fake_file = io.BytesIO(b"fake content")
    response = client.post(
        "/video/translate",
        files={"file": ("invalid.txt", fake_file, "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.text


# ----------------------------------------------------------------------
# TEST CASE 3: Corrupted or unreadable video file
# ----------------------------------------------------------------------
def test_translate_video_corrupted(tmp_path):
    """Test proper error response for a corrupted video file."""
    corrupted_path = tmp_path / "corrupted.mp4"
    with open(corrupted_path, "wb") as f:
        f.write(b"not a valid video file")

    with open(corrupted_path, "rb") as f:
        response = client.post(
            "/video/translate",
            files={"file": ("corrupted.mp4", f, "video/mp4")}
        )

    assert response.status_code == 500
    assert "failed" in response.text.lower() or "corrupted" in response.text.lower()


# ----------------------------------------------------------------------
# TEST CASE 4: No hands detected (mocked)
# ----------------------------------------------------------------------
def test_translate_video_no_hands(monkeypatch, sample_video):
    """Test the case when no hands are detected in any frame."""
    def mock_crop_hand_from_frame(frame, hands):
        return None  # Simulate no detection

    from utils import mediapipe_utils
    monkeypatch.setattr(mediapipe_utils, "crop_hand_from_frame", mock_crop_hand_from_frame)

    with open(sample_video, "rb") as f:
        response = client.post(
            "/video/translate",
            files={"file": ("temp_video.mp4", f, "video/mp4")}
        )

    assert response.status_code == 404
    assert "No hands detected" in response.text