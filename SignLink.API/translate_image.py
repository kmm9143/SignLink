# DESCRIPTION:  This script provides an API endpoint for ASL (American Sign Language) image classification.
#               It accepts an uploaded image, preprocesses it using MediaPipe to crop the hand region, and
#               then sends the cropped image to a Roboflow Inference API for ASL alphabet prediction.
#               The prediction result is returned as JSON for integration with frontend or other services.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] GeeksforGeeks. (2023, January 10). Face and hand landmarks detection using Python - Mediapipe, OpenCV. GeeksforGeeks. Retrieved September 19, 2025, from https://www.geeksforgeeks.org/machine-learning/face-and-hand-landmarks-detection-using-python-mediapipe-opencv/
#               [2] Google. (n.d.). MediaPipe Hands. MediaPipe. Retrieved September 19, 2025, from https://mediapipe.readthedocs.io/en/latest/solutions/hands.html
#               [3] Google AI Edge. (2025, January 13). Hand landmarks detection guide for Python. Google AI Edge. Retrieved September 19, 2025, from https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python
#               [4] Roboflow. (2025, February 4). Python inference-sdk. In Roboflow Documentation. Retrieved September 19, 2025, from https://docs.roboflow.com/deploy/sdks/python-inference-sdk
#               [5] Roboflow. (2025, May 16). Using the Python SDK. In Roboflow Developer Documentation. Retrieved September 19, 2025, from https://docs.roboflow.com/developer/python-sdk/using-the-python-sdk

# -------------------------------------------------------------------
# Step 1: Import required libraries
# -------------------------------------------------------------------
from fastapi import APIRouter, UploadFile, File                   # FastAPI tools for routing and file handling
from fastapi.responses import JSONResponse                        # For returning JSON API responses
import cv2                                                        # OpenCV for image decoding and processing
import numpy as np                                                # NumPy for handling image arrays

# -------------------------------------------------------------------
# Step 2: Import utility functions for MediaPipe preprocessing and Roboflow inference
# -------------------------------------------------------------------
from utils.roboflow_client import run_asl_inference               # Sends image to Roboflow for ASL prediction
from utils.mediapipe_utils import init_hands, crop_hand_from_frame  # Initialize MediaPipe & crop hand from frame

# -------------------------------------------------------------------
# Step 3: Configure FastAPI router
# -------------------------------------------------------------------
router = APIRouter(prefix="/image", tags=["image"])               # Define API router with "/image" prefix

# -------------------------------------------------------------------
# Step 4: Initialize MediaPipe hand detection for static images
# -------------------------------------------------------------------
hands = init_hands(static_image_mode=True)                       # Use static mode for single image uploads

# -------------------------------------------------------------------
# Step 5: Define API endpoint for ASL prediction
# -------------------------------------------------------------------
@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    Predict ASL letter from uploaded image using MediaPipe preprocessing and Roboflow model.
    
    Steps:
    1. Read uploaded file into memory.
    2. Decode image bytes into OpenCV BGR frame.
    3. Crop hand region using MediaPipe landmarks.
    4. Send cropped image to Roboflow for ASL prediction.
    5. Return prediction result as JSON.
    """
    
    # -------------------------------------------------------------------
    # Step 5a: Read uploaded image bytes
    # -------------------------------------------------------------------
    contents = await file.read()                                  # Read uploaded file into memory
    nparr = np.frombuffer(contents, np.uint8)                     # Convert bytes → NumPy array
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)                 # Decode image array → OpenCV BGR frame

    # -------------------------------------------------------------------
    # Step 5b: Crop hand region using MediaPipe
    # -------------------------------------------------------------------
    cropped_img = crop_hand_from_frame(frame, hands)             # Returns cropped image or None if no hand detected
    if cropped_img is None:
        return JSONResponse(content={"error": "No hand detected"}, status_code=400)  # Return error if no hand

    # -------------------------------------------------------------------
    # Step 5c: Run Roboflow ASL inference
    # -------------------------------------------------------------------
    result = run_asl_inference(cropped_img)                       # Send cropped hand to Roboflow API

    # -------------------------------------------------------------------
    # Step 5d: Return prediction result as JSON
    # -------------------------------------------------------------------
    return JSONResponse(content=result)