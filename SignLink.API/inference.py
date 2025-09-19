# DESCRIPTION: Standalone script to test Roboflow model on a local image
# LANGUAGE:    Python

from roboflow import Roboflow
import os

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0")

rf = Roboflow(api_key=ROBOFLOW_API_KEY)
project = rf.workspace().project("asl-alphabet")   # 👈 replace with your project slug
model = project.version(1).model

# Test on one image
img_path = "sample.jpg"   # 👈 replace with your test image
prediction = model.predict(img_path, confidence=40, overlap=30).json()

print("🔍 Prediction:", prediction)
if "predictions" in prediction and prediction["predictions"]:
    top = max(prediction["predictions"], key=lambda x: x["confidence"])
    print(f"✅ Predicted: {top['class']} ({top['confidence']:.2f})")
else:
    print("⚠️ No hand detected.")
