# utils/roboflow_client.py
import os
from inference_sdk import InferenceHTTPClient

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0")
WORKSPACE = "sweng894"
WORKFLOW_ID = "asl-alphabet"

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

def run_asl_inference(pil_img):
    """Send a PIL image to Roboflow and return predictions."""
    return client.run_workflow(
        workspace_name=WORKSPACE,
        workflow_id=WORKFLOW_ID,
        images={"image": pil_img},
        use_cache=True
    )