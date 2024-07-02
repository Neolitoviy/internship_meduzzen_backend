import uvicorn
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI()


@app.get("/")
def health_check():
    return {"status_code": 200,
            "detail": "ok",
            "result": "working"
            }


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
