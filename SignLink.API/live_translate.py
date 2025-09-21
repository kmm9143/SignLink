# DESCRIPTION:  This script provides a real-time ASL (American Sign Language) translation demo using webcam input.
#               It detects hands using MediaPipe, crops the hand region, and sends it to a Roboflow Inference API
#               for ASL alphabet prediction. The predicted label and confidence are displayed live on the video feed.
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
import cv2                                                      # Import OpenCV for video capture and image processing
import os                                                       # Import os for file operations
import tempfile                                                 # Import tempfile for creating temporary files
from inference_sdk import InferenceHTTPClient                   # Import Roboflow Inference client for API calls
import mediapipe as mp                                          # Import MediaPipe for hand detection

# -----------------------------------------------------------------------------------
# Step 2: Initialize Roboflow Inference client
# -----------------------------------------------------------------------------------
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",                  # Roboflow inference API endpoint
    api_key="OrkdRhEVTGpAqU13RVg0"                              # Roboflow API key (replace with your valid key)
)

# -----------------------------------------------------------------------------------
# Step 3: Initialize MediaPipe Hands
# -----------------------------------------------------------------------------------
mp_hands = mp.solutions.hands                                   # Reference to MediaPipe Hands solution
hands = mp_hands.Hands(
    static_image_mode=False,                                    # Use video stream (not static images)
    max_num_hands=1,                                            # Detect only one hand
    min_detection_confidence=0.7,                               # Minimum confidence for detection
    min_tracking_confidence=0.7                                 # Minimum confidence for tracking
)

# -----------------------------------------------------------------------------------
# Step 4: Start webcam capture
# -----------------------------------------------------------------------------------
cap = cv2.VideoCapture(0)                                       # Open the default webcam (device 0)

# -----------------------------------------------------------------------------------
# Step 5: Main loop for real-time hand detection and ASL prediction
# -----------------------------------------------------------------------------------
while True:
    ret, frame = cap.read()                                     # Read a frame from the webcam
    if not ret:                                                 # If frame not read successfully, exit loop
        break

    frame = cv2.flip(frame, 1)                                  # Flip frame horizontally for mirror effect
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)          # Convert frame to RGB for MediaPipe
    result = hands.process(rgb_frame)                           # Run hand detection

    if result.multi_hand_landmarks:                             # If at least one hand is detected
        hand_landmarks = result.multi_hand_landmarks[0]         # Get landmarks for the first detected hand

        # Get bounding box of hand
        h, w, _ = frame.shape                                  # Get frame dimensions
        x_min = int(min([lm.x for lm in hand_landmarks.landmark]) * w) # Minimum x of hand landmarks
        x_max = int(max([lm.x for lm in hand_landmarks.landmark]) * w) # Maximum x of hand landmarks
        y_min = int(min([lm.y for lm in hand_landmarks.landmark]) * h) # Minimum y of hand landmarks
        y_max = int(max([lm.y for lm in hand_landmarks.landmark]) * h) # Maximum y of hand landmarks

        pad = 20                                               # Padding around the bounding box
        x_min = max(0, x_min - pad)                            # Ensure x_min is not negative
        y_min = max(0, y_min - pad)                            # Ensure y_min is not negative
        x_max = min(w, x_max + pad)                            # Ensure x_max does not exceed frame width
        y_max = min(h, y_max + pad)                            # Ensure y_max does not exceed frame height

        # Crop hand
        hand_crop = frame[y_min:y_max, x_min:x_max]            # Crop the hand region from the frame

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file: # Create a temporary file for the cropped hand
            temp_path = tmp_file.name
            cv2.imwrite(temp_path, hand_crop)                  # Write the cropped hand image to the temp file

        # Run prediction using the temporary file
        try:
            result_rf = client.run_workflow(                   # Call Roboflow workflow for ASL prediction
                workspace_name="sweng894",                     # Roboflow workspace name
                workflow_id="asl-alphabet",                    # Roboflow workflow ID
                images={"image": temp_path},                   # Pass the cropped hand image
                use_cache=True                                 # Use cached results if available
            )

            # Extract label and confidence from nested structure
            label = "None"                                     # Default label
            confidence = 0                                     # Default confidence
            if result_rf and isinstance(result_rf, list):       # Check if result is a list
                first_item = result_rf[0]
                predictions_list = first_item.get("predictions", {}).get("predictions", [])
                if predictions_list:
                    label = predictions_list[0].get("class", "None")         # Get predicted class label
                    confidence = predictions_list[0].get("confidence", 0)    # Get prediction confidence

            # Overlay prediction
            cv2.putText(frame, f"{label} ({confidence:.2f})", (x_min, y_min-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)          # Draw label and confidence on frame

        except Exception as e:
            cv2.putText(frame, "Error", (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)          # Display error on frame
            print("Error calling Roboflow:", e)                             # Print error to console

        # Draw bounding box around hand
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0,255,0), 2)  # Draw rectangle around detected hand

        # Remove temporary file
        os.remove(temp_path)                                                # Delete the temporary image file

    cv2.imshow("ASL Live Translate", frame)                                 # Show the frame with overlays

    if cv2.waitKey(1) & 0xFF == ord('q'):                                   # Exit loop if 'q' is pressed
        break

cap.release()                                                               # Release the webcam resource
cv2.destroyAllWindows()                                                     # Close all OpenCV windows
hands.close()                                                               # Close the MediaPipe Hands instance
