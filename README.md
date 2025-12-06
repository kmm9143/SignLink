Model Extensibility Guide (US10 Modularity and Extensibility)

This guide explains how to replace the current Roboflow model in SignLink with a different model. The backend is structured so the translation process for images, video, and webcam does not depend on any specific provider. All model related work is handled through one function, which makes it easy to switch to something new without changing the rest of the system.

1. Overview of How Models Fit Into the System

When a translation request arrives, SignLink follows three main steps.

Preprocessing with MediaPipe
The system detects the hand and crops the image or video frame so the model receives only the important region.

Model Inference
The cropped image is passed into one function:

run_asl_inference(pil_img)


The rest of the application does not need to know which model is being used.

Postprocessing
The routers return a simple and consistent response for the frontend.

Since the routers only call this one function, you can replace the model by updating the function itself.

2. Where the Current Model Code Lives

The Roboflow model is defined in:

utils/roboflow_client.py


The routers import it using:

from utils.roboflow_client import run_asl_inference


This is the file that must be changed when a new model is introduced.

3. Required Format for New Models

Any new model must return the following structure:

def run_asl_inference(pil_img):
    return {
        "prediction": {
            "top": "<letter>",
            "confidence": <float>
        }
    }


The routers expect this exact format. If you provide it, everything will continue to work.

4. Steps to Add a New Model

Step 1. Create a New Model File
Create a file inside the utils folder. For example:

utils/my_new_model.py


Inside the file, provide the function:

def run_asl_inference(pil_img):
    return {
        "prediction": {
            "top": "A",
            "confidence": 0.99
        }
    }


You can write any logic you want inside the function. It can call a local model, a server, a cloud service, or any other method you choose.

Step 2. Update the Router Imports
In the translation routers:

routers/translate_image.py
routers/translate_video.py
routers/translate_webcam.py


Change the import from:

from utils.roboflow_client import run_asl_inference


to:

from utils.my_new_model import run_asl_inference


Nothing else needs to be changed.

Step 3. Restart the Backend
Once the backend restarts, your new model will automatically be used for:

• Image translation
• Video translation
• Webcam translation

All features such as saving history, text to speech, displaying confidence, buffering, and live streaming will continue working without adjustment.

5. Verification Procedure (TC US10 05)

To confirm that model replacement works as described, follow this process.

Create a mock model file named:

utils/mock_model.py


with the function:

def run_asl_inference(pil_img):
    return {
        "prediction": {
            "top": "TEST",
            "confidence": 1.0
        }
    }


Update the routers to import this file.

Run the backend and submit an image to the image prediction route.

If the response is:

{
  "prediction": {
    "top": "TEST",
    "confidence": 1.0
  }
}


and no other code changes were required, then the system meets the requirements for US10 and this test case.

6. Why This Structure Supports Easy Model Replacement

Only one file in the backend depends on a specific model.
All routers expect the same function signature, so they do not rely on any details of the model.
Preprocessing and postprocessing work the same no matter which model you use.
Models can come from any source without affecting the rest of the system.
No changes are needed in the translation flow, the database, or user settings.

Because the design keeps all model logic in a single place, replacing the model takes only a few minutes and does not introduce risk to the rest of the system.
