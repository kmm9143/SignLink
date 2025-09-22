# DESCRIPTION:  Standalone script to test a Roboflow ASL model on a local image.
#               Loads a model from Roboflow, runs inference on a sample image, and prints the result.
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
from roboflow import Roboflow   # Import Roboflow Python SDK for model access
import os                       # Import os for environment variable and file handling

# -----------------------------------------------------------------------------------
# Step 2: Set up Roboflow API key
# -----------------------------------------------------------------------------------
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0") # Get Roboflow API key from environment or use default

# -----------------------------------------------------------------------------------
# Step 3: Initialize Roboflow model
# -----------------------------------------------------------------------------------
rf = Roboflow(api_key=ROBOFLOW_API_KEY)                              # Initialize Roboflow client with API key
project = rf.workspace().project("asl-alphabet")                     # Get the ASL project (replace with your project slug if needed)
model = project.version(1).model                                     # Load version 1 of the model

# -----------------------------------------------------------------------------------
# Step 4: Run inference on a local image
# -----------------------------------------------------------------------------------
img_path = "sample.jpg"                                              # Path to the test image (replace with your image path)
prediction = model.predict(img_path, confidence=40, overlap=30).json() # Run prediction with confidence and overlap thresholds

# -----------------------------------------------------------------------------------
# Step 5: Print prediction results
# -----------------------------------------------------------------------------------
print("Prediction:", prediction)                                  # Print the full prediction JSON
if "predictions" in prediction and prediction["predictions"]:        # If predictions exist in the result
    top = max(prediction["predictions"], key=lambda x: x["confidence"]) # Get the prediction with the highest confidence
    print(f"Predicted: {top['class']} ({top['confidence']:.2f})") # Print the top predicted class and confidence
else:
    print("No hand detected.")                                    # Print warning if no predictions were found