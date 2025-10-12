# DESCRIPTION:  This script serves as a standalone verification test for the ASL preprocessing pipeline.
#               It reads a sample video, detects hands using MediaPipe, draws hand landmarks on each frame,
#               crops the detected hand regions, and saves both annotated and cropped images for analysis.
#               The test confirms that each frame containing a hand is properly detected and processed
#               before being passed to the ASL inference model.
#
# LANGUAGE:     PYTHON
#
# SOURCE(S):    [1] GeeksforGeeks. (2023, January 10). Face and hand landmarks detection using Python - Mediapipe, OpenCV.
#                   GeeksforGeeks. Retrieved October 11, 2025, from https://www.geeksforgeeks.org/machine-learning/face-and-hand-landmarks-detection-using-python-mediapipe-opencv/
#               [2] Google. (n.d.). MediaPipe Hands. MediaPipe. Retrieved October 11, 2025, from https://mediapipe.readthedocs.io/en/latest/solutions/hands.html
#               [3] Stack Overflow. (n.d.). How to crop hand region from MediaPipe landmarks in OpenCV using Python.
#                   Retrieved October 11, 2025, from https://stackoverflow.com/questions/69218223
#               [4] Roboflow. (2025, May 16). Using the Python SDK. In Roboflow Developer Documentation.
#                   Retrieved October 11, 2025, from https://docs.roboflow.com/developer/python-sdk/using-the-python-sdk
#               [5] OpenCV. (n.d.). VideoCapture Class Reference. Retrieved October 11, 2025, from https://docs.opencv.org/
#
# -------------------------------------------------------------------
# Step 1: Import required libraries
# -------------------------------------------------------------------
import os
import cv2
import json
import numpy as np
import mediapipe as mp

# -------------------------------------------------------------------
# Step 2: Import custom utility functions
# -------------------------------------------------------------------
# init_hands          - Initializes MediaPipe Hands detection pipeline
# crop_hand_from_frame - Crops detected hand region from input frame
# run_asl_inference    - Sends cropped hand(s) to Roboflow inference model
# -------------------------------------------------------------------
from utils.mediapipe_utils import init_hands, crop_hand_from_frame
from utils.roboflow_client import run_asl_inference

# -------------------------------------------------------------------
# Step 3: Initialize MediaPipe drawing and hand models
# -------------------------------------------------------------------
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# -------------------------------------------------------------------
# Step 4: Define preprocessing test function
# -------------------------------------------------------------------
def run_preprocessing_test():
    """
    Runs a preprocessing verification test to confirm that the pipeline:
    1. Detects hands using MediaPipe.
    2. Draws hand landmarks for visualization.
    3. Crops the hand region for classification.
    4. Logs and saves debug outputs for inspection.
    """
    print("[TEST] Starting preprocessing verification test (TC-US2-03)")
    print("[TEST] This will verify that frames are cropped before classification and show landmarks.")

    # -------------------------------------------------------------------
    # Step 4a: Load test video and validate file existence
    # -------------------------------------------------------------------
    video_path = "tests/ASL_Short_Video.mp4"
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Test video not found at {video_path}")

    # Initialize MediaPipe hands in static image mode (frame-by-frame)
    hands = init_hands(static_image_mode=True)
    cap = cv2.VideoCapture(video_path)

    # Initialize variables for frame counting and logging
    frame_idx = 0
    cropped_frames = []
    frame_metadata = []

    # Create debug output directory
    os.makedirs("tests/debug_outputs", exist_ok=True)

    # -------------------------------------------------------------------
    # Step 4b: Process each frame from the video
    # -------------------------------------------------------------------
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Stop when video ends

        print(f"[DEBUG] Processing frame {frame_idx}...")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        frame_info = {"frame_idx": frame_idx, "hands_detected": False, "crop_saved": False}

        # -------------------------------------------------------------------
        # Step 4c: Draw landmarks and crop detected hands
        # -------------------------------------------------------------------
        if results.multi_hand_landmarks:
            frame_info["hands_detected"] = True

            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

            # Attempt to crop hand region using helper utility
            cropped_img = crop_hand_from_frame(frame, hands)
            if cropped_img is not None:
                cropped_np = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_RGB2BGR)
                cropped_frames.append(cropped_np)
                frame_info["crop_saved"] = True
                frame_info["crop_shape"] = cropped_np.shape

                # Save cropped frame to debug folder
                cropped_path = f"tests/debug_outputs/frame_{frame_idx:03d}_cropped.jpg"
                cv2.imwrite(cropped_path, cropped_np)

            # Save annotated (with landmarks) version
            annotated_path = f"tests/debug_outputs/frame_{frame_idx:03d}_annotated.jpg"
            cv2.imwrite(annotated_path, frame)

        else:
            print(f"[DEBUG] Frame {frame_idx}: no hand detected.")

        frame_metadata.append(frame_info)
        frame_idx += 1

    # -------------------------------------------------------------------
    # Step 4d: Release video and write structured metadata
    # -------------------------------------------------------------------
    cap.release()

    metadata_path = "tests/debug_outputs/frame_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(frame_metadata, f, indent=2)

    print(f"[TEST] Total frames processed: {frame_idx}")
    detected_count = sum(1 for m in frame_metadata if m["hands_detected"])
    print(f"[TEST] Frames with hands detected: {detected_count}")

    # -------------------------------------------------------------------
    # Step 4e: Validate preprocessing results and run inference
    # -------------------------------------------------------------------
    if len(cropped_frames) == 0:
        print("[ERROR] No valid cropped frames generated — preprocessing failed.")
        return

    print("[TEST] Running dummy inference on cropped frames...")
    results = run_asl_inference(cropped_frames)

    print(f"[TEST] Inference returned {len(results)} results.")
    print("[TEST] ✅ Preprocessing pipeline verification complete.")
    print("[TEST] ✅ PASS: Each detected frame was annotated, structured, and logged.")

# -------------------------------------------------------------------
# Step 5: Execute test if script is run directly
# -------------------------------------------------------------------
if __name__ == "__main__":
    run_preprocessing_test()