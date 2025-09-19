from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import requests
import os

# Load Roboflow API key from environment variable (recommended)
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "OrkdRhEVTGpAqU13RVg0")

# Roboflow hosted API endpoint (pretrained ASL model)
ROBOFLOW_MODEL_URL = f"https://detect.roboflow.com/asl-alphabet/1?api_key={ROBOFLOW_API_KEY}"

app = FastAPI(
    title="SignLink API (Roboflow)",
    description="ASL Translation Backend using Roboflow Pretrained Model",
    version="1.0"
)

@app.post("/predict-image")
async def predict_image(file: UploadFile = File(...)):
    try:
        # Read file into memory
        img_bytes = await file.read()

        # Send to Roboflow hosted model
        resp = requests.post(
            ROBOFLOW_MODEL_URL,
            files={"file": img_bytes}
        )

        if resp.status_code != 200:
            return JSONResponse(
                content={"error": resp.text},
                status_code=resp.status_code
            )

        result = resp.json()

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
