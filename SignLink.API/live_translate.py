import cv2
import os
import tempfile
from inference_sdk import InferenceHTTPClient
import mediapipe as mp

# Initialize Roboflow Inference client
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="OrkdRhEVTGpAqU13RVg0"  # replace with your valid API key
)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]

        # Get bounding box of hand
        h, w, _ = frame.shape
        x_min = int(min([lm.x for lm in hand_landmarks.landmark]) * w)
        x_max = int(max([lm.x for lm in hand_landmarks.landmark]) * w)
        y_min = int(min([lm.y for lm in hand_landmarks.landmark]) * h)
        y_max = int(max([lm.y for lm in hand_landmarks.landmark]) * h)

        pad = 20
        x_min = max(0, x_min - pad)
        y_min = max(0, y_min - pad)
        x_max = min(w, x_max + pad)
        y_max = min(h, y_max + pad)

        # Crop hand
        hand_crop = frame[y_min:y_max, x_min:x_max]

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            temp_path = tmp_file.name
            cv2.imwrite(temp_path, hand_crop)

        # Run prediction using the temporary file
        try:
            result_rf = client.run_workflow(
                workspace_name="sweng894",
                workflow_id="asl-alphabet",
                images={"image": temp_path},
                use_cache=True
            )

            # Extract label and confidence from nested structure
            label = "None"
            confidence = 0
            if result_rf and isinstance(result_rf, list):
                first_item = result_rf[0]
                predictions_list = first_item.get("predictions", {}).get("predictions", [])
                if predictions_list:
                    label = predictions_list[0].get("class", "None")
                    confidence = predictions_list[0].get("confidence", 0)

            # Overlay prediction
            cv2.putText(frame, f"{label} ({confidence:.2f})", (x_min, y_min-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        except Exception as e:
            cv2.putText(frame, "Error", (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            print("Error calling Roboflow:", e)

        # Draw bounding box around hand
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0,255,0), 2)

        # Remove temporary file
        os.remove(temp_path)

    cv2.imshow("ASL Live Translate", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
