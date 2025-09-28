# utils/mediapipe_utils.py
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

mp_hands = mp.solutions.hands

def init_hands(static_image_mode=True):
    """Initialize MediaPipe Hands with config for images or video."""
    return mp_hands.Hands(
        static_image_mode=static_image_mode,
        max_num_hands=1,
        min_detection_confidence=0.7 if not static_image_mode else 0.5,
        min_tracking_confidence=0.7 if not static_image_mode else 0.0
    )

def crop_hand_from_frame(frame, hands):
    """Crop hand region using MediaPipe landmarks. Returns PIL image or None."""
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if not results.multi_hand_landmarks:
        return None

    lm = results.multi_hand_landmarks[0].landmark
    x_min = int(min(l.x for l in lm) * w)
    x_max = int(max(l.x for l in lm) * w)
    y_min = int(min(l.y for l in lm) * h)
    y_max = int(max(l.y for l in lm) * h)

    pad = 20
    x_min, y_min = max(0, x_min - pad), max(0, y_min - pad)
    x_max, y_max = min(w, x_max + pad), min(h, y_max + pad)

    if x_max <= x_min or y_max <= y_min:
        return None

    cropped = frame[y_min:y_max, x_min:x_max]
    return Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
