from inference_sdk import InferenceHTTPClient

# Initialize the client with your API key
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="OrkdRhEVTGpAqU13RVg0"  # your valid API key
)

# Run the pretrained ASL workflow
result = client.run_workflow(
    workspace_name="sweng894",    # your workspace
    workflow_id="asl-alphabet",   # your workflow
    images={
        "image": r"C:\Datasets\ASL_Alphabet\asl_alphabet_test\asl_alphabet_test\A_test.jpg"     # local image path or URL
    },
    use_cache=True  # caches the workflow definition for faster subsequent calls
)

# Print results
print("✅ Prediction result:")
print(result)
