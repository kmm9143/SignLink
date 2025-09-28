# DESCRIPTION:  This script provides an API endpoint for ASL (American Sign Language) image classification.
#               It accepts an uploaded image, saves it temporarily, and sends it to a Roboflow Inference API
#               for ASL alphabet prediction. The prediction result is returned as JSON for integration with
#               frontend or other services.
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

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from inference_sdk import InferenceHTTPClient
import cv2, mediapipe as mp
import numpy as np
import io
from PIL import Image
import os

router = APIRouter(prefix="/image", tags=["image"])

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0")
WORKSPACE = "sweng894"
WORKFLOW_ID = "asl-alphabet"

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

def preprocess_with_mediapipe_bytes(image_bytes: bytes):
    """Run MediaPipe on uploaded image bytes and return cropped PIL.Image."""
    # Decode bytes -> np.array
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if not results.multi_hand_landmarks:
        print("[DEBUG] No hand detected, sending original image")
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    lm = results.multi_hand_landmarks[0].landmark
    x_min = int(min(l.x for l in lm) * w)
    x_max = int(max(l.x for l in lm) * w)
    y_min = int(min(l.y for l in lm) * h)
    y_max = int(max(l.y for l in lm) * h)

    pad = 20
    x_min, y_min = max(0, x_min - pad), max(0, y_min - pad)
    x_max, y_max = min(w, x_max + pad), min(h, y_max + pad)

    if x_max <= x_min or y_max <= y_min:
        print("[DEBUG] Invalid crop, using original")
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    cropped = frame[y_min:y_max, x_min:x_max]
    return Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))

@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """Predict ASL letter from uploaded image using in-memory MediaPipe preprocessing."""
    try:
        # Read file into memory
        contents = await file.read()

        # Preprocess with MediaPipe -> cropped PIL.Image
        cropped_img = preprocess_with_mediapipe_bytes(contents)

        # Send to Roboflow directly
        result = client.run_workflow(
            workspace_name=WORKSPACE,
            workflow_id=WORKFLOW_ID,
            images={"image": cropped_img},
            use_cache=True
        )

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
