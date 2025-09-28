# DESCRIPTION:  This script provides a FastAPI WebSocket endpoint for real-time ASL (American Sign Language)
#               translation using webcam frames. It receives video frames from the frontend, detects hands
#               using MediaPipe, crops the hand region, and sends it to a Roboflow Inference API for ASL
#               alphabet prediction. The predicted label and confidence are sent back to the frontend along
#               with the annotated video frame.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] GeeksforGeeks. (2023, January 10). Face and hand landmarks detection using Python - Mediapipe, OpenCV.
#               [2] Google. (n.d.). MediaPipe Hands. MediaPipe.
#               [3] Google AI Edge. (2025, January 13). Hand landmarks detection guide for Python.
#               [4] Roboflow. (2025, February 4). Python inference-sdk. In Roboflow Documentation.
#               [5] Roboflow. (2025, May 16). Using the Python SDK. In Roboflow Developer Documentation.
#               [6] Roboflow. (n.d.). How do I run inference? Inference Documentation.
#               [7] Roboflow. (n.d.). InferencePipeline. In Roboflow Documentation.
#               [8] Warchocki, J., Vlasenko, M., & Eisma, Y. B. (2023, October 23). GRLib: An open-source hand gesture detection and recognition python library.
#               [9] Gautam, A. (2024). Hand recognition using OpenCV & MediaPipe. Medium.

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2, base64, numpy as np, io
from PIL import Image

from utils.roboflow_client import run_asl_inference
from utils.mediapipe_utils import init_hands, crop_hand_from_frame

router = APIRouter(prefix="/webcam", tags=["webcam"])
hands = init_hands(static_image_mode=False)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if not data.startswith("data:image"):
                continue

            base64_data = data.split(",")[1]
            img_bytes = base64.b64decode(base64_data)
            img_array = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            cropped_img = crop_hand_from_frame(frame, hands)
            prediction_data = None
            if cropped_img:
                prediction_data = run_asl_inference(cropped_img)

            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())
            await websocket.send_json({"prediction": prediction_data})

    except WebSocketDisconnect:
        pass
