# DESCRIPTION:  This script defines a FastAPI backend for American Sign Language (ASL) image classification
#               using a Roboflow-hosted pretrained model. It exposes endpoints for image, video, and webcam
#               uploads, sends the data to the Roboflow API, and returns the prediction results as JSON.
#               It also integrates centralized error handling from error_handler.py for consistent responses.
# LANGUAGE:     PYTHON

# -----------------------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -----------------------------------------------------------------------------------
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import routers
from routers.translate_image import router as image_router
from routers.translate_video import router as video_router
from routers.translate_webcam import router as webcam_router
from routers.settings import router as settings_router
from routers.translation_history import router as history_router
from routers.auth import router as auth_router

# Database setup
from database import engine, Base

# Import centralized error handler
from utils.error_handler import register_exception_handlers

# -----------------------------------------------------------------------------------
# Step 2: Initialize FastAPI application
# -----------------------------------------------------------------------------------
app = FastAPI(title="SignLink API")

# Register global exception handlers (centralized)
register_exception_handlers(app)

# -----------------------------------------------------------------------------------
# Step 3: Configure CORS (Cross-Origin Resource Sharing)
# -----------------------------------------------------------------------------------
origins = [
    "http://localhost:51233",
    "http://127.0.0.1:51233",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------------
# Step 4: Logging Configuration
# -----------------------------------------------------------------------------------
logger = logging.getLogger("signlink")
handler = logging.FileHandler("error.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

# -----------------------------------------------------------------------------------
# Step 5: Include Routers
# -----------------------------------------------------------------------------------
app.include_router(image_router)
app.include_router(video_router)
app.include_router(webcam_router)
app.include_router(settings_router)
app.include_router(history_router)
app.include_router(auth_router)

# -----------------------------------------------------------------------------------
# Step 6: Health Check Endpoint
# -----------------------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}

# -----------------------------------------------------------------------------------
# Step 7: WebSocket Endpoint for Real-time Webcam Translation
# -----------------------------------------------------------------------------------
@app.websocket("/webcam/ws")
async def webcam_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {repr(e)}")
        await websocket.close(code=1011, reason="Internal server error")