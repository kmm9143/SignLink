# DESCRIPTION:  This FastAPI router handles uploaded video files and performs ASL (American Sign Language)
#               translation by processing video frames at intervals. For each frame, it detects hands using
#               MediaPipe, crops the hand region, and sends it to the Roboflow API for ASL alphabet prediction.
#               Results include predicted labels and confidence scores for each timestamp.
#               Additional error handling added for corrupted or unreadable video files.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] GeeksforGeeks. (2023, January 10). Face and hand landmarks detection using Python - Mediapipe, OpenCV. GeeksforGeeks. Retrieved September 19, 2025, from https://www.geeksforgeeks.org/machine-learning/face-and-hand-landmarks-detection-using-python-mediapipe-opencv/
#               [2] Google. (n.d.). MediaPipe Hands. MediaPipe. Retrieved September 19, 2025, from https://mediapipe.readthedocs.io/en/latest/solutions/hands.html
#               [3] Google AI Edge. (2025, January 13). Hand landmarks detection guide for Python. Google AI Edge. Retrieved September 19, 2025, from https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python
#               [4] Roboflow. (2025, February 4). Python inference-sdk. In Roboflow Documentation. Retrieved September 19, 2025, from https://docs.roboflow.com/deploy/sdks/python-inference-sdk
#               [5] Roboflow. (2025, May 16). Using the Python SDK. In Roboflow Developer Documentation. Retrieved September 19, 2025, from https://docs.roboflow.com/developer/python-sdk/using-the-python-sdk
#               [6] Stack Overflow. (2025). How to detect and handle corrupted video files in OpenCV. Retrieved October 12, 2025, from https://stackoverflow.com/questions/  

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import tempfile
import os
from utils.mediapipe_utils import init_hands, crop_hand_from_frame
from utils.roboflow_client import run_asl_inference

router = APIRouter(prefix="/video", tags=["video"])

# Initialize MediaPipe in static image mode for batch frame analysis
hands = init_hands(static_image_mode=True)

@router.post("/translate")
async def translate_video(file: UploadFile = File(...)):
    """
    Handles video upload for ASL translation.
    Steps:
    1. Save uploaded file temporarily.
    2. Extract frames every N milliseconds.
    3. Use MediaPipe to detect hand(s) in each frame.
    4. Crop hand and run ASL inference on Roboflow.
    5. Return list of predictions with timestamps.
    6. Handle errors for corrupted or unreadable videos.
    """

    # ----------------------------------------------------------------------
    # Step 1: Validate uploaded file type
    # ----------------------------------------------------------------------
    valid_types = ["video/mp4", "video/avi", "video/mov", "video/quicktime"]
    if file.content_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an MP4, AVI, or MOV video.")

    # ----------------------------------------------------------------------
    # Step 2: Save to temporary file
    # ----------------------------------------------------------------------
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded video: {e}")

    # ----------------------------------------------------------------------
    # Step 3: Open video for processing with error handling
    # ----------------------------------------------------------------------
    cap = cv2.VideoCapture(tmp_path)
    if not cap.isOpened():
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail="Failed to open video file for reading. The file may be corrupted or unreadable.")

    # Check for minimal frames (corrupted or empty video detection)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count == 0:
        cap.release()
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail="Video contains no frames. The file may be corrupted.")

    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    if frame_rate == 0:
        frame_rate = 30  # fallback in case metadata is missing

    frame_interval = int(frame_rate * 0.5)  # Process every 0.5 seconds
    frame_idx = 0
    predictions = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                # Could indicate end of file or corrupted frame
                break

            if frame_idx % frame_interval == 0:
                # ----------------------------------------------------------------------
                # Step 4: Detect and crop hand(s)
                # ----------------------------------------------------------------------
                cropped_img = crop_hand_from_frame(frame, hands)
                if cropped_img is not None:
                    # ----------------------------------------------------------------------
                    # Step 5: Run ASL prediction via Roboflow
                    # ----------------------------------------------------------------------
                    pred = run_asl_inference(cropped_img)
                    predictions.append({
                        "frame": frame_idx,
                        "timestamp_sec": round(frame_idx / frame_rate, 2),
                        "prediction": pred
                    })

            frame_idx += 1

    finally:
        cap.release()
        os.remove(tmp_path)

    # ----------------------------------------------------------------------
    # Step 6: Return JSON response or error if no hands detected
    # ----------------------------------------------------------------------
    if not predictions:
        raise HTTPException(status_code=404, detail="No hands detected in video or video may be corrupted.")

    return JSONResponse(content={"predictions": predictions})