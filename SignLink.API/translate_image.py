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

# -----------------------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -----------------------------------------------------------------------------------
from fastapi import APIRouter, UploadFile, File                        # FastAPI router and file upload support
from fastapi.responses import JSONResponse                             # For returning JSON responses
import tempfile                                                        # For creating temporary files
import os                                                              # For environment variables and file operations
from inference_sdk import InferenceHTTPClient                          # Roboflow Inference client for API calls

# Extra imports for preprocessing
import cv2                                                             # OpenCV for image manipulation
import mediapipe as mp                                                 # MediaPipe for hand detection

# -----------------------------------------------------------------------------------
# Step 2: Initialize API router and Roboflow client
# -----------------------------------------------------------------------------------
router = APIRouter(prefix="/image", tags=["image"])                    # Create router for image endpoints

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0") # Get Roboflow API key from environment or use default
WORKSPACE = "sweng894"                                                 # Roboflow workspace name
WORKFLOW_ID = "asl-alphabet"                                           # Roboflow workflow ID

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",                         # Roboflow inference API endpoint
    api_key=ROBOFLOW_API_KEY                                           # Roboflow API key
)

# -----------------------------------------------------------------------------------
# Step 3: MediaPipe Hand Preprocessing Function
# -----------------------------------------------------------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.3  # relaxed sensitivity
)

drawing_utils = mp.solutions.drawing_utils

def preprocess_with_mediapipe(image_path: str) -> str:
    """
    Detects a hand in the image using MediaPipe and crops the bounding box.
    Saves an overlay for debugging.
    Returns the path of the cropped image, or the original if no hand detected.
    """
    try:
        image = cv2.imread(image_path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)

        if not results.multi_hand_landmarks:
            print(f"[DEBUG] No hand detected in {image_path}, sending original image")
            return image_path

        # Get bounding box from hand landmarks
        h, w, _ = image.shape
        hand = results.multi_hand_landmarks[0]

        x_min = min([lm.x for lm in hand.landmark]) * w
        y_min = min([lm.y for lm in hand.landmark]) * h
        x_max = max([lm.x for lm in hand.landmark]) * w
        y_max = max([lm.y for lm in hand.landmark]) * h

        # Crop safely (clamp to image size)
        x_min, y_min = max(int(x_min), 0), max(int(y_min), 0)
        x_max, y_max = min(int(x_max), w), min(int(y_max), h)

        cropped = image[y_min:y_max, x_min:x_max]

        # Save cropped version
        cropped_path = image_path.replace(".jpg", "_cropped.jpg")
        cv2.imwrite(cropped_path, cropped)

        # Save debug overlay with landmarks drawn
        for hand_landmarks in results.multi_hand_landmarks:
            drawing_utils.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        overlay_path = image_path.replace(".jpg", "_overlay.jpg")
        cv2.imwrite(overlay_path, image)

        print(f"[DEBUG] Hand detected, cropped image saved at {cropped_path}")
        print(f"[DEBUG] Overlay with landmarks saved at {overlay_path}")

        return cropped_path

    except Exception as e:
        print(f"[DEBUG] Preprocessing failed: {e}, sending original image")
        return image_path

# -----------------------------------------------------------------------------------
# Step 4: Define image prediction endpoint
# -----------------------------------------------------------------------------------
@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    Predict ASL letter from uploaded image with MediaPipe preprocessing.
    """
    try:
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            tmp_file.write(await file.read())
            temp_path = tmp_file.name

        # Run preprocessing step
        cropped_path = preprocess_with_mediapipe(temp_path)

        # Run Roboflow workflow for ASL prediction
        result = client.run_workflow(
            workspace_name=WORKSPACE,
            workflow_id=WORKFLOW_ID,
            images={"image": cropped_path},
            use_cache=True
        )

        # Cleanup (keep overlay for debug, remove temp + cropped)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if cropped_path != temp_path and os.path.exists(cropped_path):
            os.remove(cropped_path)

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
