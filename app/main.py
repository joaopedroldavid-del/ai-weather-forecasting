from fastapi import FastAPI

from app.config.settings import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
