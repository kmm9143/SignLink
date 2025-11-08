# DESCRIPTION:  FastAPI WebSocket endpoint for real-time ASL translation using webcam frames.
#               Receives video frames from the frontend, detects hands using MediaPipe, crops
#               the hand region, sends it to Roboflow Inference API for ASL prediction, and
#               returns annotated frames and predictions to the frontend.
# LANGUAGE:     PYTHON
# SOURCE(S):    See original sources for MediaPipe and Roboflow usage.

# -------------------------------------------------------------------
# Step 1: Import required libraries
# -------------------------------------------------------------------
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import base64
import numpy as np
from PIL import Image
import requests  # Added for backend connection/timeout error handling
import json
import logging

# -------------------------------------------------------------------
# Step 2: Import utility functions for MediaPipe preprocessing and Roboflow inference
# -------------------------------------------------------------------
from utils.roboflow_client import run_asl_inference
from utils.mediapipe_utils import init_hands, crop_hand_from_frame

# -------------------------------------------------------------------
# Step 3: Configure FastAPI router
# -------------------------------------------------------------------
router = APIRouter(prefix="/webcam", tags=["webcam"])

# -------------------------------------------------------------------
# Step 4: Initialize MediaPipe hand detection for continuous video
# -------------------------------------------------------------------
hands = init_hands(static_image_mode=False)

# -------------------------------------------------------------------
# Step 5: Define WebSocket endpoint for real-time ASL prediction
# -------------------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles real-time ASL predictions from webcam video stream.
    Includes error handling for backend inference timeouts or failures.
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            if not data.startswith("data:image"):
                continue

            # -------------------------------------------------------------------
            # Step 5a: Decode base64 frame into OpenCV BGR image
            # -------------------------------------------------------------------
            try:
                base64_data = data.split(",")[1]
                img_bytes = base64.b64decode(base64_data)
                img_array = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if frame is None:
                    raise ValueError("Decoded frame is None")
            except Exception as e:
                logging.error(f"Frame decoding failed: {e}")
                try:
                    await websocket.send_json({"error": "Invalid image frame received."})
                except Exception:
                    logging.error("Failed to send JSON error for invalid frame")
                continue

            # -------------------------------------------------------------------
            # Step 5b: Crop hand region using MediaPipe
            # -------------------------------------------------------------------
            cropped_img = crop_hand_from_frame(frame, hands)

            if cropped_img is not None and isinstance(cropped_img, Image.Image):
                cropped_img = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_RGB2BGR)

            prediction_data = None

            # -------------------------------------------------------------------
            # Step 5c: Run ASL inference with backend error handling
            # -------------------------------------------------------------------
            if isinstance(cropped_img, np.ndarray) and cropped_img.size > 0:
                try:
                    prediction_data = run_asl_inference(cropped_img)

                except requests.exceptions.ConnectionError:
                    logging.warning("Inference server unavailable.")
                    await websocket.send_json({
                        "error": "Server unavailable. Please try again later."
                    })
                    continue  # Skip sending frame

                except requests.exceptions.Timeout:
                    logging.warning("Inference request timed out.")
                    await websocket.send_json({
                        "error": "The request to the inference server timed out."
                    })
                    continue  # Skip sending frame

                except Exception as e:
                    logging.error(f"Unexpected inference error: {e}")
                    await websocket.send_json({
                        "error": "Unexpected server error during inference."
                    })
                    continue  # Skip sending frame

            # -------------------------------------------------------------------
            # Step 5d: Send annotated frame and prediction back to frontend
            # Only send the frame if inference succeeded
            # -------------------------------------------------------------------
            if prediction_data is not None:
                try:
                    _, buffer = cv2.imencode(".jpg", frame)
                    await websocket.send_bytes(buffer.tobytes())
                except Exception as e:
                    logging.error(f"WebSocket send frame error: {e}")

                # Send prediction JSON
                try:
                    await websocket.send_json({"prediction": prediction_data})
                except Exception as e:
                    logging.error(f"WebSocket send JSON error: {e}")
                    try:
                        await websocket.send_json({"error": "Error sending prediction data."})
                    except Exception:
                        logging.error("Failed to send fallback JSON error")

            # -------------------------------------------------------------------
            # Step 5e: Handle the case where inference was not performed
            # -------------------------------------------------------------------
            elif cropped_img is None or not isinstance(cropped_img, np.ndarray):
                await websocket.send_json({"error": "No hand detected or invalid image."})

    except WebSocketDisconnect:
        logging.info("Client disconnected from WebSocket.")
    except Exception as e:
        logging.error(f"Unexpected WebSocket error: {e}")
        try:
            await websocket.send_json({"error": "Server error. Please try again later."})
        except Exception:
            logging.error("Failed to send JSON error for unexpected WebSocket exception")
