from fastapi import FastAPI

from app.config.settings import get_settings
from app.controllers.forecast_controller import router as forecast_router
from app.controllers.health_controller import router as health_router

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(forecast_router)
