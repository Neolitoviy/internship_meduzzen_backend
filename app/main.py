import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # All
    allow_credentials=True,
    allow_methods=["*"],  # All
    allow_headers=["*"],  # All
)


@app.get("/")
def health_check():
    return {"status_code": 200,
            "detail": "ok",
            "result": "working"
            }


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
