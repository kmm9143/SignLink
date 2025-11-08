# DESCRIPTION:  FastAPI WebSocket endpoint for real-time ASL translation using webcam frames.
#               Receives video frames from the frontend, detects hands using MediaPipe, crops
#               the hand region, sends it to Roboflow Inference API for ASL prediction, and
#               returns annotated frames and predictions to the frontend.
# LANGUAGE:     PYTHON
# SOURCE(S):    See original sources for MediaPipe and Roboflow usage.

# -------------------------------------------------------------------
# Step 1: Import required libraries
# -------------------------------------------------------------------
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import base64
import numpy as np
from PIL import Image

# -------------------------------------------------------------------
# Step 2: Import utility functions for MediaPipe preprocessing and Roboflow inference
# -------------------------------------------------------------------
from utils.roboflow_client import run_asl_inference
from utils.mediapipe_utils import init_hands, crop_hand_from_frame

# -------------------------------------------------------------------
# Step 3: Configure FastAPI router
# -------------------------------------------------------------------
router = APIRouter(prefix="/webcam", tags=["webcam"])

# -------------------------------------------------------------------
# Step 4: Initialize MediaPipe hand detection for continuous video
# -------------------------------------------------------------------
hands = init_hands(static_image_mode=False)

# -------------------------------------------------------------------
# Step 5: Define WebSocket endpoint for real-time ASL prediction
# -------------------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles real-time ASL predictions from webcam video stream.
    """

    await websocket.accept()

    try:
        while True:
            prediction_data = None
            frame = None

            try:
                data = await websocket.receive_text()
                
                # Only process if frame is a valid base64 image
                if data.startswith("data:image"):
                    base64_data = data.split(",")[1]
                    img_bytes = base64.b64decode(base64_data)
                    img_array = np.frombuffer(img_bytes, np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                    # Crop hand region using MediaPipe
                    cropped_img = crop_hand_from_frame(frame, hands)

                    # Convert PIL.Image to NumPy array if needed
                    if cropped_img is not None and isinstance(cropped_img, Image.Image):
                        cropped_img = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_RGB2BGR)

                    # Run ASL inference if a valid hand region is detected
                    if isinstance(cropped_img, np.ndarray) and cropped_img.size > 0:
                        prediction_data = run_asl_inference(cropped_img)

                else:
                    # Invalid frame: create dummy black frame to respond
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)

            except Exception:
                # Catch any decoding, crop, or inference error
                prediction_data = None
                if frame is None:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # Send annotated frame and prediction back to frontend
            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())
            await websocket.send_json({"prediction": prediction_data})

    except WebSocketDisconnect:
        pass
