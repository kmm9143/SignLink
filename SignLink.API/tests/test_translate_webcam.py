from fastapi import FastAPI
from translate_webcam import router as webcam_router
import uvicorn

app = FastAPI()
app.include_router(webcam_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003, reload=True)