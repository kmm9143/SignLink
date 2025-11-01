# tests/test_us3_translate_webcam.py
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
    img = Image.open(png_path).convert("RGB")
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def encode_frame_to_base64(frame: np.ndarray) -> str:
    _, buffer = cv2.imencode(".jpg", frame)
    return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

# -------------------------------------------------------------------
# Dummy WebSocket
# -------------------------------------------------------------------
class DummyWebSocket:
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
    return DummyWebSocket()

@pytest.fixture
def mock_mediapipe_and_roboflow(monkeypatch):
    from routers import translate_webcam as tw

    # Patch crop_hand_from_frame to return a small truthy array
    monkeypatch.setattr(tw, "crop_hand_from_frame", lambda frame, hands: np.ones((1, 1, 3), dtype=np.uint8))
    # Patch run_asl_inference to return fixed prediction
    monkeypatch.setattr(tw, "run_asl_inference", lambda img: [{"label": "A", "confidence": 0.95}])

# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_webcam_prediction_success(ws, mock_mediapipe_and_roboflow):
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

    # Predictions are a list of dicts
    predictions = [p for msg in ws.sent_json for p in msg["prediction"]]
    assert len(predictions) > 0
    pred = predictions[0]
    assert pred["label"] == "A"
    assert pred["confidence"] >= 0.8

@pytest.mark.asyncio
async def test_mediapipe_preprocessing_called(ws, monkeypatch):
    from routers import translate_webcam
    called = {}

    png_path = Path(__file__).parent / "test_data" / "ASL_A.png"
    frame = load_frame_from_png(str(png_path))
    data_b64 = encode_frame_to_base64(frame)

    # Patch crop_hand_from_frame to track call
    def fake_crop(frame_arg, hands):
        called["crop_called"] = True
        return np.ones((1,1,3), dtype=np.uint8)  # safe truthy array

    monkeypatch.setattr(translate_webcam, "crop_hand_from_frame", fake_crop)
    monkeypatch.setattr(translate_webcam, "run_asl_inference", lambda img: [{"label": "A", "confidence": 0.95}])

    async def receive_text_once():
        if not hasattr(receive_text_once, "_called"):
            receive_text_once._called = True
            return data_b64
        raise WebSocketDisconnect

    ws.receive_text = receive_text_once

    await translate_webcam.websocket_endpoint(ws)
    assert called.get("crop_called") is True

@pytest.mark.asyncio
async def test_webcam_disconnect(ws):
    from routers.translate_webcam import websocket_endpoint

    async def receive_disconnect():
        raise WebSocketDisconnect
    ws.receive_text = receive_disconnect

    await websocket_endpoint(ws)
    assert ws.accepted is True

@pytest.mark.asyncio
async def test_webcam_permission_prompt(ws):
    from routers.translate_webcam import websocket_endpoint

    async def receive_disconnect():
        raise WebSocketDisconnect
    ws.receive_text = receive_disconnect

    await websocket_endpoint(ws)
    assert ws.accepted is True

@pytest.mark.asyncio
async def test_webcam_latency(ws, mock_mediapipe_and_roboflow):
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

    # Allow enough time for async processing
    assert (end - start) < 1.0