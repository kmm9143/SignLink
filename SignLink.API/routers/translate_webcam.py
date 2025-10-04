# DESCRIPTION:  This script provides a FastAPI WebSocket endpoint for real-time ASL (American Sign Language)
#               translation using webcam frames. It receives video frames from the frontend, detects hands
#               using MediaPipe, crops the hand region, and sends it to a Roboflow Inference API for ASL
#               alphabet prediction. The predicted label and confidence are sent back to the frontend along
#               with the annotated video frame.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] GeeksforGeeks. (2023, January 10). Face and hand landmarks detection using Python - Mediapipe, OpenCV. GeeksforGeeks. Retrieved September 19, 2025, from https://www.geeksforgeeks.org/machine-learning/face-and-hand-landmarks-detection-using-python-mediapipe-opencv/
#               [2] Google. (n.d.). MediaPipe Hands. MediaPipe. Retrieved September 19, 2025, from https://mediapipe.readthedocs.io/en/latest/solutions/hands.html
#               [3] Google AI Edge. (2025, January 13). Hand landmarks detection guide for Python. Google AI Edge. Retrieved September 19, 2025, from https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python
#               [4] Roboflow. (2025, February 4). Python inference-sdk. In Roboflow Documentation. Retrieved September 19, 2025, from https://docs.roboflow.com/deploy/sdks/python-inference-sdk
#               [5] Roboflow. (2025, May 16). Using the Python SDK. In Roboflow Developer Documentation. Retrieved September 19, 2025, from https://docs.roboflow.com/developer/python-sdk/using-the-python-sdk

# -------------------------------------------------------------------
# Step 1: Import required libraries
# -------------------------------------------------------------------
from fastapi import APIRouter, WebSocket, WebSocketDisconnect     # FastAPI WebSocket tools
import cv2                                                        # OpenCV for image decoding and processing
import base64                                                     # Base64 decoding for incoming frames
import numpy as np                                                # NumPy for handling image arrays
import io                                                         # For converting byte streams to images
from PIL import Image                                             # Pillow for image handling

# -------------------------------------------------------------------
# Step 2: Import utility functions for MediaPipe preprocessing and Roboflow inference
# -------------------------------------------------------------------
from utils.roboflow_client import run_asl_inference               # Sends image to Roboflow for ASL prediction
from utils.mediapipe_utils import init_hands, crop_hand_from_frame  # Initialize MediaPipe & crop hand from frame

# -------------------------------------------------------------------
# Step 3: Configure FastAPI router
# -------------------------------------------------------------------
router = APIRouter(prefix="/webcam", tags=["webcam"])             # Define API router with "/webcam" prefix

# -------------------------------------------------------------------
# Step 4: Initialize MediaPipe hand detection for continuous video
# -------------------------------------------------------------------
hands = init_hands(static_image_mode=False)                       # Use dynamic mode for real-time webcam frames

# -------------------------------------------------------------------
# Step 5: Define WebSocket endpoint for real-time ASL prediction
# -------------------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles real-time ASL predictions from webcam video stream using a WebSocket connection.

    Steps:
    1. Accept WebSocket connection from frontend.
    2. Continuously receive base64-encoded frames.
    3. Decode frames into OpenCV images.
    4. Crop hand region using MediaPipe landmarks.
    5. Send cropped hand to Roboflow for prediction.
    6. Return annotated frame and prediction JSON to frontend.
    """

    # -------------------------------------------------------------------
    # Step 5a: Accept WebSocket connection
    # -------------------------------------------------------------------
    await websocket.accept()                                       # Accept the WebSocket connection

    try:
        # -------------------------------------------------------------------
        # Step 5b: Continuously process incoming frames
        # -------------------------------------------------------------------
        while True:
            data = await websocket.receive_text()                  # Receive base64-encoded frame as text
            if not data.startswith("data:image"):                  # Skip invalid data
                continue

            # -------------------------------------------------------------------
            # Step 5c: Decode base64 frame into OpenCV BGR image
            # -------------------------------------------------------------------
            base64_data = data.split(",")[1]                       # Extract base64 string
            img_bytes = base64.b64decode(base64_data)              # Decode base64 → raw bytes
            img_array = np.frombuffer(img_bytes, np.uint8)         # Convert bytes → NumPy array
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)      # Decode array → OpenCV BGR frame

            # -------------------------------------------------------------------
            # Step 5d: Crop hand region using MediaPipe
            # -------------------------------------------------------------------
            cropped_img = crop_hand_from_frame(frame, hands)       # Crop hand or return None
            prediction_data = None
            if cropped_img:                                        # If a hand is detected
                prediction_data = run_asl_inference(cropped_img)   # Send to Roboflow for ASL prediction

            # -------------------------------------------------------------------
            # Step 5e: Send annotated frame and prediction back to frontend
            # -------------------------------------------------------------------
            _, buffer = cv2.imencode(".jpg", frame)                # Encode frame to JPEG
            await websocket.send_bytes(buffer.tobytes())          # Send annotated video frame
            await websocket.send_json({"prediction": prediction_data})  # Send prediction JSON

    except WebSocketDisconnect:
        # -------------------------------------------------------------------
        # Step 5f: Handle client disconnect gracefully
        # -------------------------------------------------------------------
        pass