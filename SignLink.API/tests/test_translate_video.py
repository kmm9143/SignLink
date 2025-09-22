from fastapi import FastAPI
from translate_video import router as video_router
import uvicorn

app = FastAPI()
app.include_router(video_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True)
