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
import os                                                             # For environment variables and file operations
from inference_sdk import InferenceHTTPClient                          # Roboflow Inference client for API calls

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
# Step 3: Define image prediction endpoint
# -----------------------------------------------------------------------------------
@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    Predict ASL letter from uploaded image.

    Parameters:
    - file: UploadFile: The image file uploaded by the user.

    Returns:
    - JSONResponse: A response containing the prediction result or error message.
    """
    try:
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            tmp_file.write(await file.read())                          # Write uploaded image to temp file
            temp_path = tmp_file.name                                  # Store temp file path

        # Run Roboflow workflow for ASL prediction
        result = client.run_workflow(
            workspace_name=WORKSPACE,                                  # Roboflow workspace name
            workflow_id=WORKFLOW_ID,                                   # Roboflow workflow ID
            images={"image": temp_path},                               # Pass image file path
            use_cache=True                                             # Use cached results if available
        )

        os.remove(temp_path)                                           # Delete temporary image file
        return JSONResponse(content=result)                            # Return prediction result as JSON

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500) # Return error as JSON if exception occurs