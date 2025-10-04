# DESCRIPTION:  This script provides an API endpoint for ASL (American Sign Language) video classification.
#               It accepts an uploaded video, extracts frames, and sends each frame to a Roboflow Inference API
#               for ASL alphabet prediction. The prediction results for all frames are returned as JSON for
#               integration with frontend or other services.
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
import os                                                             # For environment variables and file operations
import cv2                                                            # OpenCV for video and image processing
from inference_sdk import InferenceHTTPClient                          # Roboflow Inference client for API calls

# -----------------------------------------------------------------------------------
# Step 2: Initialize API router and Roboflow client
# -----------------------------------------------------------------------------------
router = APIRouter(prefix="/video", tags=["video"])                    # Create router for video endpoints

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0") # Get Roboflow API key from environment or use default
WORKSPACE = "sweng894"                                                 # Roboflow workspace name
WORKFLOW_ID = "asl-alphabet"                                           # Roboflow workflow ID

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",                         # Roboflow inference API endpoint
    api_key=ROBOFLOW_API_KEY                                           # Roboflow API key
)

# -----------------------------------------------------------------------------------
# Step 3: Define video prediction endpoint
# -----------------------------------------------------------------------------------
@router.post("/predict")
async def predict_video(file: UploadFile = File(...)):
    """
    Predict ASL signs in an uploaded video file.
    
    Args:
        file (UploadFile): The video file uploaded by the user.

    Returns:
        JSONResponse: A response containing the predictions or an error message.
    """
    try:
        # Save uploaded video temporarily
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
            tmp_file.write(await file.read())                          # Write uploaded video to temp file
            video_path = tmp_file.name                                 # Store temp file path

        cap = cv2.VideoCapture(video_path)                             # Open video file for reading frames
        predictions = []                                               # List to store predictions for each frame

        while True:
            ret, frame = cap.read()                                    # Read a frame from the video
            if not ret:                                                # If no more frames, exit loop
                break

            # Save frame as temporary image
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_img:
                frame_path = tmp_img.name
                cv2.imwrite(frame_path, frame)                         # Write frame to temp image file

            # Run Roboflow workflow for ASL prediction
            result = client.run_workflow(
                workspace_name=WORKSPACE,                              # Roboflow workspace name
                workflow_id=WORKFLOW_ID,                               # Roboflow workflow ID
                images={"image": frame_path},                          # Pass frame image file
                use_cache=True                                         # Use cached results if available
            )
            predictions.append(result)                                 # Store prediction result
            os.remove(frame_path)                                      # Delete temporary frame image file

        cap.release()                                                  # Release video capture resource
        os.remove(video_path)                                          # Delete temporary video file

        return JSONResponse(content={"predictions": predictions})      # Return all predictions as JSON

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500) # Return error as JSON if exception occurs
