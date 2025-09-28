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

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import mediapipe as mp
import numpy as np
import base64
import io
import os
import logging
from PIL import Image
from inference_sdk import InferenceHTTPClient

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.ERROR)  # Only log errors
logger = logging.getLogger("asl-webcam")

# -----------------------------------------------------------------------------
# Step 1: Setup router, Roboflow client, and MediaPipe Hands
# -----------------------------------------------------------------------------
router = APIRouter(prefix="/webcam", tags=["webcam"])

# Roboflow Inference client setup
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0")
WORKSPACE = "sweng894"
WORKFLOW_ID = "asl-alphabet"
client = InferenceHTTPClient(api_url="https://serverless.roboflow.com", api_key=ROBOFLOW_API_KEY)

# MediaPipe Hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)

# -----------------------------------------------------------------------------
# Step 2: Define WebSocket endpoint
# -----------------------------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # -----------------------------------------------------------------
            # Step 2a: Receive base64 frame
            # -----------------------------------------------------------------
            data = await websocket.receive_text()
            if not data.startswith("data:image"):
                continue

            # Decode base64 → bytes → np.array → OpenCV frame
            base64_data = data.split(",")[1]
            img_bytes = base64.b64decode(base64_data)
            img_array = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is None:
                logger.error("Failed to decode frame")
                continue

            # -----------------------------------------------------------------
            # Step 2b: Run MediaPipe Hand Detection
            # -----------------------------------------------------------------
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            prediction_data = None
            if results.multi_hand_landmarks:
                # Get bounding box
                lm = results.multi_hand_landmarks[0].landmark
                x_min = int(min([l.x for l in lm]) * w)
                x_max = int(max([l.x for l in lm]) * w)
                y_min = int(min([l.y for l in lm]) * h)
                y_max = int(max([l.y for l in lm]) * h)

                pad = 20
                x_min, y_min = max(0, x_min - pad), max(0, y_min - pad)
                x_max, y_max = min(w, x_max + pad), min(h, y_max + pad)

                # -----------------------------------------------------------------
                # Step 2c: Validate crop and send to Roboflow
                # -----------------------------------------------------------------
                if x_max > x_min and y_max > y_min:
                    hand_crop = frame[y_min:y_max, x_min:x_max]

                    if hand_crop.size > 0:
                        _, buffer = cv2.imencode(".jpg", hand_crop)
                        pil_img = Image.open(io.BytesIO(buffer.tobytes()))

                        try:
                            result_rf = client.run_workflow(
                                workspace_name=WORKSPACE,
                                workflow_id=WORKFLOW_ID,
                                images={"image": pil_img},
                                use_cache=True,
                            )
                            prediction_data = result_rf
                        except Exception as e:
                            logger.error(f"Roboflow call failed: {e}")

                # Draw bounding box
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            # -----------------------------------------------------------------
            # Step 2d: Send back frame + prediction
            # -----------------------------------------------------------------
            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())  # annotated frame
            await websocket.send_json({"prediction": prediction_data})  # JSON prediction

    except WebSocketDisconnect:
        pass