# DESCRIPTION:  Utility module to handle Roboflow API inference for ASL (American Sign Language) prediction.
#               Provides a function to send a PIL image to a Roboflow workflow and return prediction results.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] Roboflow. (2025, February 4). Python inference-sdk. In Roboflow Documentation. Retrieved September 19, 2025, from https://docs.roboflow.com/deploy/sdks/python-inference-sdk
#               [2] Roboflow. (2025, May 16). Using the Python SDK. In Roboflow Developer Documentation. Retrieved September 19, 2025, from https://docs.roboflow.com/developer/python-sdk/using-the-python-sdk

# -------------------------------------------------------------------
# Step 1: Import required libraries
# -------------------------------------------------------------------
import os
from inference_sdk import InferenceHTTPClient   # Roboflow SDK client for making inference requests

# -------------------------------------------------------------------
# Step 2: Configure Roboflow API credentials and workflow
# -------------------------------------------------------------------
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")  # Load API key from environment or default
WORKSPACE = "sweng894"                            # Workspace name on Roboflow
WORKFLOW_ID = "asl-alphabet"                      # Workflow ID for ASL alphabet prediction

# -------------------------------------------------------------------
# Step 3: Initialize Roboflow Inference Client
# -------------------------------------------------------------------
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",  # Base API URL
    api_key=ROBOFLOW_API_KEY                     # API key for authentication
)

# -------------------------------------------------------------------
# Step 4: Define function to run ASL inference
# -------------------------------------------------------------------
def run_asl_inference(pil_img):
    """
    Send a PIL.Image object to the Roboflow workflow and return predictions.

    Args:
        pil_img (PIL.Image.Image): Image of a hand to classify ASL letter.

    Returns:
        dict: Prediction results from Roboflow workflow.
    """
    return client.run_workflow(
        workspace_name=WORKSPACE,        # Specify workspace
        workflow_id=WORKFLOW_ID,         # Specify workflow
        images={"image": pil_img},       # Provide the image as input
        use_cache=True                   # Use cached predictions if available
    )