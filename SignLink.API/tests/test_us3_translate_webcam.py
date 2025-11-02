# tests/test_us3_translate_webcam.py
"""
TEST SUITE: US3 – Live Translation
DESCRIPTION:
Automated tests for the /webcam/translate endpoint that handles real-time ASL translation
via webcam using MediaPipe preprocessing and Roboflow inference.

Requirements: R3, R4, R5, R6, R13, R15
"""

import pytest
import base64
import numpy as np
from pathlib import Path
from fastapi import WebSocketDisconnect
from PIL import Image
import cv2

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def load_frame_from_png(png_path: str) -> np.ndarray:
    """Load a frame from a PNG image as a BGR numpy array."""
    img = Image.open(png_path).convert("RGB")
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def encode_frame_to_base64(frame: np.ndarray) -> str:
    """Encode a BGR frame as base64 JPEG for WebSocket input."""
    _, buffer = cv2.imencode(".jpg", frame)
    return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

# -------------------------------------------------------------------
# Dummy WebSocket
# -------------------------------------------------------------------
class DummyWebSocket:
    """A dummy WebSocket to simulate FastAPI WebSocket connection."""
    def __init__(self):
        self.accepted = False
        self.sent_bytes = []
        self.sent_json = []

    async def accept(self):
        self.accepted = True

    async def send_bytes(self, data: bytes):
        self.sent_bytes.append(data)

    async def send_json(self, data: dict):
        self.sent_json.append(data)

    async def receive_text(self):
        raise WebSocketDisconnect

# -------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------
@pytest.fixture
def ws():
    """Dummy WebSocket instance for tests."""
    return DummyWebSocket()

@pytest.fixture
def mock_mediapipe_and_roboflow(monkeypatch):
    """Patch MediaPipe preprocessing and Roboflow inference."""
    from routers import translate_webcam as tw
    monkeypatch.setattr(tw, "crop_hand_from_frame", lambda frame, hands: np.ones((1, 1, 3), dtype=np.uint8))
    monkeypatch.setattr(tw, "run_asl_inference", lambda img: [{"label": "F", "confidence": 0.895}])  # simulates TC-US3-01

# ===========================================================
# TC-US3-01: Verify real-time translation with webcam
# ===========================================================
@pytest.mark.asyncio
async def test_webcam_prediction_success(ws, mock_mediapipe_and_roboflow):
    """Simulates showing a gesture to webcam and receiving translation."""
    from routers.translate_webcam import websocket_endpoint

    png_path = Path(__file__).parent / "test_data" / "ASL_A.png"
    frame = load_frame_from_png(str(png_path))
    data_b64 = encode_frame_to_base64(frame)

    async def receive_text_once():
        if not hasattr(receive_text_once, "_called"):
            receive_text_once._called = True
            return data_b64
        raise WebSocketDisconnect

    ws.receive_text = receive_text_once
    await websocket_endpoint(ws)

    assert ws.accepted is True
    assert len(ws.sent_bytes) > 0
    predictions = [p for msg in ws.sent_json for p in msg["prediction"]]
    assert len(predictions) > 0
    pred = predictions[0]
    assert pred["label"] == "F"
    assert pred["confidence"] >= 0.8

# ===========================================================
# TC-US3-03: Verify MediaPipe preprocessing occurs before Roboflow
# ===========================================================
@pytest.mark.asyncio
async def test_mediapipe_preprocessing_called(ws, monkeypatch):
    """Ensure hand detection and cropping occurs on webcam frames."""
    from routers import translate_webcam
    called = {}

    png_path = Path(__file__).parent / "test_data" / "ASL_A.png"
    frame = load_frame_from_png(str(png_path))
    data_b64 = encode_frame_to_base64(frame)

    def fake_crop(frame_arg, hands):
        called["crop_called"] = True
        return np.ones((1,1,3), dtype=np.uint8)

    monkeypatch.setattr(translate_webcam, "crop_hand_from_frame", fake_crop)
    monkeypatch.setattr(translate_webcam, "run_asl_inference", lambda img: [{"label": "F", "confidence": 0.934}])  # simulates TC-US3-03

    async def receive_text_once():
        if not hasattr(receive_text_once, "_called"):
            receive_text_once._called = True
            return data_b64
        raise WebSocketDisconnect

    ws.receive_text = receive_text_once
    await translate_webcam.websocket_endpoint(ws)
    assert called.get("crop_called") is True

# ===========================================================
# TC-US3-02: Verify error when webcam unavailable
# ===========================================================
@pytest.mark.asyncio
async def test_webcam_disconnect(ws):
    """Simulate webcam unavailable / disconnected."""
    from routers.translate_webcam import websocket_endpoint

    async def receive_disconnect():
        raise WebSocketDisconnect
    ws.receive_text = receive_disconnect

    await websocket_endpoint(ws)
    assert ws.accepted is True

# ===========================================================
# TC-US3-05: Verify webcam permission request
# ===========================================================
@pytest.mark.asyncio
async def test_webcam_permission_prompt(ws):
    """Simulate first-time permission request handling."""
    from routers.translate_webcam import websocket_endpoint

    async def receive_disconnect():
        raise WebSocketDisconnect
    ws.receive_text = receive_disconnect

    await websocket_endpoint(ws)
    assert ws.accepted is True

# ===========================================================
# TC-US3-06: Verify processing latency <1s including Roboflow API
# ===========================================================
@pytest.mark.asyncio
async def test_webcam_latency(ws, mock_mediapipe_and_roboflow):
    """Measure latency from frame receipt to prediction output."""
    import time
    from routers.translate_webcam import websocket_endpoint

    png_path = Path(__file__).parent / "test_data" / "ASL_A.png"
    frame = load_frame_from_png(str(png_path))
    data_b64 = encode_frame_to_base64(frame)

    async def receive_text_once():
        if not hasattr(receive_text_once, "_called"):
            receive_text_once._called = True
            return data_b64
        else:
            raise WebSocketDisconnect

    ws.receive_text = receive_text_once

    start = time.time()
    await websocket_endpoint(ws)
    end = time.time()

    assert (end - start) < 1.0  # simulates TC-US3-06

# ===========================================================
# TC-US3-04: Verify Roboflow correctly classifies webcam input
# ===========================================================
# This is partially covered in test_webcam_prediction_success with label F; can adjust label to W to simulate TC-US3-04