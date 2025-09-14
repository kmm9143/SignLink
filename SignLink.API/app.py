# DESCRIPTION:  This script defines a FastAPI backend for American Sign Language (ASL) image classification.
#               It loads a trained CNN model, exposes an endpoint for image upload and prediction, and returns
#               the predicted ASL class and confidence. The API preprocesses incoming images and uses the model
#               for inference. Designed for integration with frontend or other services.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] GeeksforGeeks. (2025, July 23). Python FastAPI tutorial. GeeksforGeeks. Retrieved September 14, 2025, from https://www.geeksforgeeks.org/python/fastapi-uvicorn/
#               [2] GeeksforGeeks. (2025, July 23). TensorFlow tutorial. GeeksforGeeks. Retrieved September 14, 2025, from https://www.geeksforgeeks.org/deep-learning/tensorflow/
#               [3] W3Schools. (2025). NumPy tutorial. W3Schools. Retrieved September 14, 2025, from https://www.w3schools.com/python/numpy/default.asp
#               [4] GeeksforGeeks. (2025, July 23). Python Pillow tutorial. GeeksforGeeks. Retrieved September 14, 2025, from https://www.geeksforgeeks.org/python/python-pillow-tutorial/
#               [5] Uvicorn. (n.d.). Uvicorn: ASGI server implementation for Python. Uvicorn. Retrieved September 14, 2025, from https://www.uvicorn.org/

# -----------------------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -----------------------------------------------------------------------------------
from fastapi import FastAPI, UploadFile, File                        # Import FastAPI and file upload utilities
from fastapi.responses import JSONResponse                           # Import JSONResponse for API responses
from tensorflow.keras.models import load_model                       # Import Keras model loader
from tensorflow.keras.preprocessing import image                     # Import image preprocessing utilities
import numpy as np                                                   # Import NumPy for numerical operations
import uvicorn                                                       # Import Uvicorn for running the ASGI server
import io                                                            # Import io for byte stream handling
from PIL import Image                                                # Import PIL for image manipulation

# -----------------------------------------------------------------------------------
# Step 2: Initialize FastAPI app
# -----------------------------------------------------------------------------------
app = FastAPI(title="SignLink API",                                  # Create FastAPI app instance
              description="ASL Translation Backend",                 # Set API description
              version="1.0")                                         # Set API version

# -----------------------------------------------------------------------------------
# Step 3: Load trained model
# -----------------------------------------------------------------------------------
MODEL_PATH = "../SignLink.Training/saved_models/asl_cnn_model.h5"    # Path to the trained Keras model file
model = load_model(MODEL_PATH)                                       # Load the trained model from disk

print("Model output shape:", model.output_shape)                     # Print model output shape for debugging

# -----------------------------------------------------------------------------------
# Step 4: Define class labels
# -----------------------------------------------------------------------------------
CLASS_LABELS = [                                                     # List of class labels for ASL prediction
    'A','B','C','D','E','F','G','H','I','J',
    'K','L','M','N','O','P','Q','R','S','T',
    'U','V','W','X','Y','Z','del','nothing','space'
] # Example for ASL alphabet

# -----------------------------------------------------------------------------------
# Step 5: Define image preprocessing function
# -----------------------------------------------------------------------------------
def preprocess_image(img: Image.Image, target_size=(64, 64)):        # Preprocess the uploaded image for the model
    """Preprocess the uploaded image for the model."""
    img = img.convert("RGB")                                         # Convert image to RGB format
    img = img.resize(target_size)                                    # Resize image to target size
    img_array = image.img_to_array(img) / 255.0                      # Convert image to array and normalize pixel values
    img_array = np.expand_dims(img_array, axis=0)                    # Add batch dimension
    return img_array                                                 # Return preprocessed image array

# -----------------------------------------------------------------------------------
# Step 6: Define prediction endpoint
# -----------------------------------------------------------------------------------
@app.post("/predict-image")                                          # Define POST endpoint for image prediction
async def predict_image(file: UploadFile = File(...)):               # Async function to handle image upload and prediction
    try:
        # Read image
        contents = await file.read()                                 # Read uploaded file contents as bytes
        img = Image.open(io.BytesIO(contents))                       # Open image from byte stream

        # Preprocess
        img_array = preprocess_image(img)                            # Preprocess image for model input

        # Predict
        preds = model.predict(img_array)                             # Get prediction probabilities from model
        predicted_class = CLASS_LABELS[np.argmax(preds)]             # Get class label with highest probability
        confidence = float(np.max(preds))                            # Get confidence score for prediction

        return JSONResponse(content={                                # Return prediction and confidence as JSON
            "prediction": predicted_class,
            "confidence": round(confidence, 4)
        })
    except Exception as e:                                           # Handle exceptions during prediction
        return JSONResponse(content={"error": str(e)}, status_code=500) # Return error message as JSON

# -----------------------------------------------------------------------------------
# Step 7: Run the API server (development mode)
# -----------------------------------------------------------------------------------
if __name__ == "__main__":                                           # Run this block only if script is executed directly
    import uvicorn                                                   # Import uvicorn for running the server
    uvicorn.run(
        "app:app",                # tells uvicorn to look for `app` inside app.py
        host="127.0.0.1",         # bind to localhost instead of 0.0.0.0
        port=8000,                # set server port
        reload=True               # auto-reload on code changes (useful in dev)
    )