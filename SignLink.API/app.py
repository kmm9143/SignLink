from fastapi import FastAPI, UploadFile, File                        # Import FastAPI and file upload utilities
from fastapi.responses import JSONResponse                           # Import JSONResponse for API responses
import requests                                                     # Import requests for HTTP requests to Roboflow API
import os                                                           # Import os for environment variable access

# DESCRIPTION:  This script defines a FastAPI backend for American Sign Language (ASL) image classification
#               using a Roboflow-hosted pretrained model. It exposes an endpoint for image upload, sends the
#               image to the Roboflow API, and returns the prediction result as JSON. Designed for integration
#               with frontend or other services for real-time ASL translation.
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
from fastapi import FastAPI, UploadFile, File                        # Import FastAPI and file upload utilities
from fastapi.responses import JSONResponse                           # Import JSONResponse for API responses
import requests                                                     # Import requests for HTTP requests to Roboflow API
import os                                                           # Import os for environment variable access

# -----------------------------------------------------------------------------------
# Step 2: Load Roboflow API key and set model endpoint
# -----------------------------------------------------------------------------------
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0") # Get Roboflow API key from environment or use default
ROBOFLOW_MODEL_URL = f"https://detect.roboflow.com/asl-alphabet/1?api_key={ROBOFLOW_API_KEY}" # Roboflow hosted API endpoint for ASL model

# -----------------------------------------------------------------------------------
# Step 3: Initialize FastAPI app
# -----------------------------------------------------------------------------------
app = FastAPI(
    title="SignLink API (Roboflow)",                                 # Set API title
    description="ASL Translation Backend using Roboflow Pretrained Model", # Set API description
    version="1.0"                                                    # Set API version
)

# -----------------------------------------------------------------------------------
# Step 4: Define image prediction endpoint
# -----------------------------------------------------------------------------------
@app.post("/predict-image")                                          # Define POST endpoint for image prediction
async def predict_image(file: UploadFile = File(...)):               # Async function to handle image upload and prediction
    try:
        # Read file into memory
        img_bytes = await file.read()                                # Read uploaded file contents as bytes

        # Send to Roboflow hosted model
        resp = requests.post(                                        # Send POST request to Roboflow API
            ROBOFLOW_MODEL_URL,
            files={"file": img_bytes}
        )

        if resp.status_code != 200:                                  # If Roboflow API returns error
            return JSONResponse(
                content={"error": resp.text},                        # Return error message as JSON
                status_code=resp.status_code
            )

        result = resp.json()                                         # Parse JSON response from Roboflow

        return JSONResponse(content=result)                          # Return prediction result as JSON

    except Exception as e:                                           # Handle exceptions during prediction
        return JSONResponse(content={"error": str(e)}, status_code=500) # Return error message as JSON

# -----------------------------------------------------------------------------------
# Step 5: Run the API server (development mode)
# -----------------------------------------------------------------------------------
if __name__ == "__main__":                                           # Run this block only if script is executed directly
    import uvicorn                                                   # Import uvicorn for running the server
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True) # Start FastAPI server with auto-reload
