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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect         # Import FastAPI for building the API server
from fastapi.middleware.cors import CORSMiddleware                  # Import CORS middleware for cross-origin requests

from routers.translate_image import router as image_router                  # Import image translation router
from routers.translate_video import router as video_router                  # Import video translation router
from routers.translate_webcam import router as webcam_router                # Import webcam translation router
from routers.settings import router as settings_router
from routers.auth import router as auth_router

from database import engine, Base
# -----------------------------------------------------------------------------------
# Step 2: Initialize FastAPI application
# -----------------------------------------------------------------------------------
app = FastAPI(title="SignLink API")                                 # Create FastAPI app instance with a title

# -----------------------------------------------------------------------------------
# Step 3: Configure CORS (Cross-Origin Resource Sharing)
# -----------------------------------------------------------------------------------
origins = [
    "http://localhost:51232",                                       # Allow local frontend (localhost)
    "http://127.0.0.1:51232"                                        # Allow local frontend (127.0.0.1)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,                                          # Restrict allowed origins (use ["*"] for all during testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------------
# Step 4: Include API routers for different translation modes
# -----------------------------------------------------------------------------------
app.include_router(image_router)                                # image translation
app.include_router(video_router)                                # video translation
app.include_router(webcam_router)                               # webcam translation
app.include_router(settings_router)                             # user settings
app.include_router(auth_router, prefix="/auth", tags=["auth"])  # authentication

# -----------------------------------------------------------------------------------
# Step 5: Health Check Endpoint
# -----------------------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}

# -----------------------------------------------------------------------------------
# Step 6: WebSocket Endpoint for Real-time Webcam Translation
# -----------------------------------------------------------------------------------
@app.websocket("/webcam/ws")
async def webcam_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()  # Receive data from frontend
            # For now, just echo it back (you can add ASL prediction later)
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        print("WebSocket client disconnected")