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
#               [6] Roboflow. (n.d.). How do I run inference? Inference Documentation. Retrieved September 19, 2025, from https://inference.roboflow.com/quickstart/inference_101/
#               [7] Roboflow. (n.d.). InferencePipeline. In Roboflow Documentation. Retrieved September 19, 2025, from https://inference.roboflow.com/using_inference/inference_pipeline/
#               [8] Warchocki, J., Vlasenko, M., & Eisma, Y. B. (2023, October 23). GRLib: An open-source hand gesture detection and recognition python library. arXiv. Retrieved September 19, 2025, from https://arxiv.org/abs/2310.14919
#               [9] Gautam, A. (2024). Hand recognition using OpenCV & MediaPipe. Medium. Retrieved September 19, 2025, from https://medium.com/aditee-gautam/hand-recognition-using-opencv-a7b109941c88

# -----------------------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -----------------------------------------------------------------------------------
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import mediapipe as mp
import tempfile
import os
from inference_sdk import InferenceHTTPClient
import numpy as np

# -----------------------------------------------------------------------------------
# Step 2: Initialize API router, Roboflow client, and MediaPipe Hands
# -----------------------------------------------------------------------------------
router = APIRouter(prefix="/webcam", tags=["webcam"])                  # Create router for webcam endpoints

# Roboflow Inference client setup
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0") # Get Roboflow API key from environment or use default
WORKSPACE = "sweng894"                                                 # Roboflow workspace name
WORKFLOW_ID = "asl-alphabet"                                           # Roboflow workflow ID
client = InferenceHTTPClient(api_url="https://serverless.roboflow.com", api_key=ROBOFLOW_API_KEY)

# MediaPipe Hands setup
mp_hands = mp.solutions.hands                                          # Reference to MediaPipe Hands solution
hands = mp_hands.Hands(
    static_image_mode=False,                                           # Use video stream (not static images)
    max_num_hands=1,                                                   # Detect only one hand
    min_detection_confidence=0.7,                                      # Minimum confidence for detection
    min_tracking_confidence=0.7                                        # Minimum confidence for tracking
)

# -----------------------------------------------------------------------------------
# Step 3: Define WebSocket endpoint for real-time webcam translation
# -----------------------------------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()                                           # Accept WebSocket connection
    try:
        while True:
            # Receive raw frame from frontend
            frame_bytes = await websocket.receive_bytes()              # Receive frame as bytes
            np_arr = np.frombuffer(frame_bytes, np.uint8)             # Convert bytes to NumPy array
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)            # Decode image from array
            h, w, _ = frame.shape                                     # Get frame dimensions

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)        # Convert frame to RGB for MediaPipe
            results = hands.process(rgb_frame)                        # Run hand detection

            prediction_data = None
            if results.multi_hand_landmarks:                          # If at least one hand is detected
                lm = results.multi_hand_landmarks[0].landmark         # Get landmarks for the first detected hand

                # Get bounding box of hand
                x_min = int(min([l.x for l in lm]) * w)
                x_max = int(max([l.x for l in lm]) * w)
                y_min = int(min([l.y for l in lm]) * h)
                y_max = int(max([l.y for l in lm]) * h)
                pad = 20
                x_min, y_min = max(0, x_min - pad), max(0, y_min - pad)
                x_max, y_max = min(w, x_max + pad), min(h, y_max + pad)

                # Crop hand and save temp image for Roboflow
                hand_crop = frame[y_min:y_max, x_min:x_max]           # Crop the hand region from the frame
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                    cv2.imwrite(tmp_file.name, hand_crop)             # Write cropped hand image to temp file
                    temp_path = tmp_file.name

                try:
                    # Run Roboflow workflow for ASL prediction
                    result_rf = client.run_workflow(
                        workspace_name=WORKSPACE,                    # Roboflow workspace name
                        workflow_id=WORKFLOW_ID,                     # Roboflow workflow ID
                        images={"image": temp_path},                 # Pass cropped hand image
                        use_cache=True                               # Use cached results if available
                    )
                    prediction_data = result_rf                      # Store prediction result
                except Exception as e:
                    print("Roboflow error:", e)                      # Print error if Roboflow call fails
                finally:
                    os.remove(temp_path)                             # Delete temporary image file

                # Draw bounding box on frame
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0,255,0), 2) # Draw rectangle around detected hand

            # Encode frame back to bytes to send to frontend
            _, buffer = cv2.imencode(".jpg", frame)                  # Encode frame as JPEG
            await websocket.send_bytes(buffer.tobytes())             # Send annotated frame to frontend
            
            # Send prediction as separate JSON message
            await websocket.send_json({"prediction": prediction_data}) # Send prediction result as JSON

    except WebSocketDisconnect:
        print("Client disconnected")                                 # Handle client disconnect
