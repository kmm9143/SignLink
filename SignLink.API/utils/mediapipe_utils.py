# DESCRIPTION:  Utility module for handling MediaPipe hand detection and preprocessing.
#               Provides functions to initialize MediaPipe Hands and crop hand regions
#               from images or video frames for ASL (American Sign Language) prediction.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] GeeksforGeeks. (2023, January 10). Face and hand landmarks detection using Python - Mediapipe, OpenCV. Retrieved September 19, 2025, from https://www.geeksforgeeks.org/machine-learning/face-and-hand-landmarks-detection-using-python-mediapipe-opencv/
#               [2] Google. (n.d.). MediaPipe Hands. MediaPipe. Retrieved September 19, 2025, from https://mediapipe.readthedocs.io/en/latest/solutions/hands.html
#               [3] Google AI Edge. (2025, January 13). Hand landmarks detection guide for Python. Retrieved September 19, 2025, from https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python

# -------------------------------------------------------------------
# Step 1: Import required libraries
# -------------------------------------------------------------------
import cv2                  # OpenCV for image processing
import mediapipe as mp       # MediaPipe for hand detection
import numpy as np           # NumPy for array operations
from PIL import Image        # Pillow for converting images

# -------------------------------------------------------------------
# Step 2: Define MediaPipe hands solution reference
# -------------------------------------------------------------------
mp_hands = mp.solutions.hands

# -------------------------------------------------------------------
# Step 3: Initialize MediaPipe Hands
# -------------------------------------------------------------------
def init_hands(static_image_mode=True):
    """
    Initialize MediaPipe Hands solution with configuration for either static images or video.

    Args:
        static_image_mode (bool): True for images, False for video streaming.

    Returns:
        mp.solutions.hands.Hands: Configured MediaPipe Hands object.
    """
    return mp_hands.Hands(
        static_image_mode=static_image_mode,                          # Image vs. video mode
        max_num_hands=1,                                               # Track only one hand
        min_detection_confidence=0.7 if not static_image_mode else 0.5, # Detection confidence threshold
        min_tracking_confidence=0.7 if not static_image_mode else 0.0  # Tracking confidence for video mode
    )

# -------------------------------------------------------------------
# Step 4: Crop hand region from a frame
# -------------------------------------------------------------------
def crop_hand_from_frame(frame, hands):
    """
    Detect and crop the hand region from a frame using MediaPipe landmarks.

    Args:
        frame (np.ndarray): OpenCV BGR image array.
        hands (mp.solutions.hands.Hands): Initialized MediaPipe Hands object.

    Returns:
        PIL.Image.Image or None: Cropped hand image as PIL Image, or None if no hand detected.
    """
    h, w, _ = frame.shape

    # Convert BGR to RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hands
    results = hands.process(rgb)

    # Return None if no hands detected
    if not results.multi_hand_landmarks:
        return None

    # Extract landmarks for first detected hand
    lm = results.multi_hand_landmarks[0].landmark

    # Compute bounding box from landmarks
    x_min = int(min(l.x for l in lm) * w)
    x_max = int(max(l.x for l in lm) * w)
    y_min = int(min(l.y for l in lm) * h)
    y_max = int(max(l.y for l in lm) * h)

    # Add padding around the bounding box
    pad = 20
    x_min, y_min = max(0, x_min - pad), max(0, y_min - pad)
    x_max, y_max = min(w, x_max + pad), min(h, y_max + pad)

    # Validate bounding box dimensions
    if x_max <= x_min or y_max <= y_min:
        return None

    # Crop hand region and convert to PIL Image
    cropped = frame[y_min:y_max, x_min:x_max]
    return Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))