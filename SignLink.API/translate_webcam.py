# DESCRIPTION:  This script provides a FastAPI WebSocket endpoint for real-time ASL (American Sign Language)
#               translation using webcam frames. It receives video frames from the frontend, detects hands
#               using MediaPipe, crops the hand region, and sends it to a Roboflow Inference API for ASL
#               alphabet prediction. The predicted label and confidence are sent back to the frontend along
#               with the annotated video frame.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] GeeksforGeeks. (2023, January 10). Face and hand landmarks detection using Python - Mediapipe, OpenCV.
#               [2] Google. (n.d.). MediaPipe Hands. MediaPipe.
#               [3] Google AI Edge. (2025, January 13). Hand landmarks detection guide for Python.
#               [4] Roboflow. (2025, February 4). Python inference-sdk. In Roboflow Documentation.
#               [5] Roboflow. (2025, May 16). Using the Python SDK. In Roboflow Developer Documentation.
#               [6] Roboflow. (n.d.). How do I run inference? Inference Documentation.
#               [7] Roboflow. (n.d.). InferencePipeline. In Roboflow Documentation.
#               [8] Warchocki, J., Vlasenko, M., & Eisma, Y. B. (2023, October 23). GRLib: An open-source hand gesture detection and recognition python library.
#               [9] Gautam, A. (2024). Hand recognition using OpenCV & MediaPipe. Medium.

# -----------------------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -----------------------------------------------------------------------------------
from fastapi import APIRouter, WebSocket, WebSocketDisconnect          # FastAPI WebSocket tools
import cv2                                                             # OpenCV for image decoding and processing
import mediapipe as mp                                                 # MediaPipe for real-time hand detection
import numpy as np                                                     # NumPy for handling image arrays
import base64                                                          # Base64 decoding for incoming frames
import io                                                              # For converting byte streams to images
import os                                                              # For environment variable access
import logging                                                         # Logging for debugging and error tracking
from PIL import Image                                                  # Pillow for image handling
from inference_sdk import InferenceHTTPClient                          # Roboflow inference client

# -----------------------------------------------------------------------------------
# Step 2: Configure logging
# -----------------------------------------------------------------------------------
logging.basicConfig(level=logging.ERROR)                               # Log only errors to reduce noise
logger = logging.getLogger("asl-webcam")                               # Create a named logger for this module

# -----------------------------------------------------------------------------------
# Step 3: Initialize API router, Roboflow client, and MediaPipe
# -----------------------------------------------------------------------------------
router = APIRouter(prefix="/webcam", tags=["webcam"])                  # Define API router with "/webcam" prefix

# Roboflow client configuration
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0")  # Load Roboflow API key from environment
WORKSPACE = "sweng894"                                                 # Roboflow workspace
WORKFLOW_ID = "asl-alphabet"                                           # Workflow ID for ASL prediction
client = InferenceHTTPClient(                                          # Initialize Roboflow HTTP client
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

# MediaPipe Hands configuration for continuous video detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,                                           # Enable continuous tracking mode
    max_num_hands=1,                                                  # Track only one hand for performance
    min_detection_confidence=0.7,                                     # Confidence threshold for detection
    min_tracking_confidence=0.7                                       # Confidence threshold for tracking
)

# -----------------------------------------------------------------------------------
# Step 4: Define WebSocket endpoint for real-time ASL prediction
# -----------------------------------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles real-time ASL predictions from webcam video stream using a WebSocket connection."""
    await websocket.accept()                                           # Accept the WebSocket connection from frontend

    try:
        # -------------------------------------------------------------------------
        # Step 4a: Continuously receive and process frames from the frontend
        # -------------------------------------------------------------------------
        while True:
            data = await websocket.receive_text()                      # Receive base64-encoded frame as text
            if not data.startswith("data:image"):                      # Skip invalid data
                continue

            # ---------------------------------------------------------------------
            # Step 4b: Decode base64 frame into OpenCV image
            # ---------------------------------------------------------------------
            base64_data = data.split(",")[1]                           # Extract base64 string (skip MIME header)
            img_bytes = base64.b64decode(base64_data)                  # Decode base64 → raw bytes
            img_array = np.frombuffer(img_bytes, np.uint8)             # Convert bytes → NumPy array
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)          # Decode image array → OpenCV BGR frame

            if frame is None:
                logger.error("Failed to decode frame")                 # Log decoding error
                continue

            # ---------------------------------------------------------------------
            # Step 4c: Run MediaPipe hand detection
            # ---------------------------------------------------------------------
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)         # Convert frame to RGB for MediaPipe
            results = hands.process(rgb_frame)                         # Detect hands in the frame

            prediction_data = None                                     # Placeholder for Roboflow prediction result

            # ---------------------------------------------------------------------
            # Step 4d: If a hand is detected, crop the region
            # ---------------------------------------------------------------------
            if results.multi_hand_landmarks:
                # Compute bounding box from landmark points
                lm = results.multi_hand_landmarks[0].landmark
                x_min = int(min([l.x for l in lm]) * w)
                x_max = int(max([l.x for l in lm]) * w)
                y_min = int(min([l.y for l in lm]) * h)
                y_max = int(max([l.y for l in lm]) * h)

                pad = 20                                               # Add padding around bounding box
                x_min, y_min = max(0, x_min - pad), max(0, y_min - pad)
                x_max, y_max = min(w, x_max + pad), min(h, y_max + pad)

                # -----------------------------------------------------------------
                # Step 4e: Validate crop and send hand image to Roboflow
                # -----------------------------------------------------------------
                if x_max > x_min and y_max > y_min:                     # Ensure valid crop region
                    hand_crop = frame[y_min:y_max, x_min:x_max]         # Crop hand from frame

                    if hand_crop.size > 0:
                        # Encode crop → bytes → PIL image (for Roboflow)
                        _, buffer = cv2.imencode(".jpg", hand_crop)
                        pil_img = Image.open(io.BytesIO(buffer.tobytes()))

                        try:
                            # Send cropped image to Roboflow for ASL prediction
                            result_rf = client.run_workflow(
                                workspace_name=WORKSPACE,
                                workflow_id=WORKFLOW_ID,
                                images={"image": pil_img},
                                use_cache=True,
                            )
                            prediction_data = result_rf                # Store prediction result
                        except Exception as e:
                            logger.error(f"Roboflow call failed: {e}") # Log API errors

                # Draw bounding box around detected hand on the original frame
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            # ---------------------------------------------------------------------
            # Step 4f: Send annotated frame and prediction back to frontend
            # ---------------------------------------------------------------------
            _, buffer = cv2.imencode(".jpg", frame)                     # Encode frame to JPEG
            await websocket.send_bytes(buffer.tobytes())               # Send processed video frame
            await websocket.send_json({"prediction": prediction_data}) # Send prediction JSON payload

    except WebSocketDisconnect:
        # Gracefully handle client disconnect
        pass