import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.dtos.forecast_request_dto import ForecastRequestDTO
from app.dtos.forecast_response_dto import ForecastConditionsDTO, ForecastResponseDTO
from app.services import forecast_service
from app.services.exceptions import InsufficientHistoricalDataError, UnsupportedLocationError

logger = logging.getLogger(__name__)

router = APIRouter()

DATE_FORMAT = "%m-%d-%Y"


@router.post("/forecast", response_model=ForecastResponseDTO)
def create_forecast(request: ForecastRequestDTO) -> ForecastResponseDTO:
    try:
        target_date = datetime.strptime(request.date, DATE_FORMAT).date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format, expected {DATE_FORMAT}")

    try:
        forecast = forecast_service.generate_forecast(request.location, target_date)
    except UnsupportedLocationError:
        raise HTTPException(status_code=404, detail=f"Location '{request.location}' is not supported")
    except InsufficientHistoricalDataError:
        raise HTTPException(
            status_code=404, detail="No historical data available for this location and date"
        )
    except Exception:
        logger.exception("Failed to generate forecast for %s on %s", request.location, request.date)
        raise HTTPException(status_code=500, detail="Internal server error")

    return ForecastResponseDTO(
        location=forecast.city,
        date=request.date,
        forecast=ForecastConditionsDTO(
            temperature_max=forecast.temperature_max_avg_c,
            temperature_min=forecast.temperature_min_avg_c,
            temperature_avg=forecast.temperature_avg_c,
            wind_speed=forecast.wind_speed_kmh,
            forecast=forecast.condition,
            precipitation=forecast.precipitation_avg_mm,
            years=forecast.years,
        ),
        narrative=forecast.narrative,
    )
