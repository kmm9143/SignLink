from fastapi import FastAPI
from translate_image import router as image_router
import uvicorn

app = FastAPI()
app.include_router(image_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)