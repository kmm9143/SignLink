import cv2
import base64
from io import BytesIO
from PIL import Image
from inference_sdk import InferenceHTTPClient
import mediapipe as mp

# Initialize Roboflow client
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="OrkdRhEVTGpAqU13RVg0"
)

# Mediapipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,  # track only one hand
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)
frame_count = 0
skip_frames = 5
last_prediction = "Waiting..."
last_confidence = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    frame_count += 1

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        # Get bounding box
        h, w, _ = frame.shape
        x_min = min([lm.x for lm in hand_landmarks.landmark]) * w
        y_min = min([lm.y for lm in hand_landmarks.landmark]) * h
        x_max = max([lm.x for lm in hand_landmarks.landmark]) * w
        y_max = max([lm.y for lm in hand_landmarks.landmark]) * h

        # Add some padding
        pad = 20
        x_min, y_min = max(0, int(x_min - pad)), max(0, int(y_min - pad))
        x_max, y_max = min(w, int(x_max + pad)), min(h, int(y_max + pad))

        # Crop hand
        hand_crop = frame[y_min:y_max, x_min:x_max]

        # Only run inference every few frames
        if frame_count % skip_frames == 0:
            # Resize for faster inference
            resized = cv2.resize(hand_crop, (224, 224))
            img_pil = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

            # Convert to base64
            buffered = BytesIO()
            img_pil.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Run Roboflow workflow
            result = client.run_workflow(
                workspace_name="sweng894",
                workflow_id="asl-alphabet",
                images={"image": img_str},
                use_cache=True
            )

            # Extract prediction safely
            try:
                last_prediction = result[0]["label"]
                last_confidence = result[0].get("confidence", 0)
            except (IndexError, KeyError, TypeError):
                last_prediction = "None"
                last_confidence = 0

        # Draw bounding box and hand landmarks
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

    # Display prediction
    cv2.putText(frame, f"{last_prediction} ({last_confidence:.2f})", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("ASL Live Translate", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
