from datetime import date

from app.ai.weather_forecast_chain import generate_narrative
from app.dtos.weather_forecast_dto import WeatherForecastDTO
from app.services import weather_statistics_service

CONFIDENCE_LOW_MAX_YEARS = 2
CONFIDENCE_MEDIUM_MAX_YEARS = 5


def _confidence_level(years_analyzed: int) -> str:
    if years_analyzed <= CONFIDENCE_LOW_MAX_YEARS:
        return "low"
    if years_analyzed <= CONFIDENCE_MEDIUM_MAX_YEARS:
        return "medium"
    return "high"


def generate_forecast(city: str, target_date: date) -> WeatherForecastDTO:
    stats = weather_statistics_service.compute_statistics(city, target_date.month, target_date.day)
    narrative = generate_narrative(stats)

    return WeatherForecastDTO(
        city=stats.city,
        target_date=target_date,
        years_analyzed=stats.years_analyzed,
        confidence=_confidence_level(stats.years_analyzed),
        temperature_avg_c=stats.temperature_avg_c,
        temperature_max_avg_c=stats.temperature_max_avg_c,
        temperature_min_avg_c=stats.temperature_min_avg_c,
        precipitation_chance_pct=stats.precipitation_chance_pct,
        precipitation_avg_mm=stats.precipitation_avg_mm,
        humidity_avg_pct=stats.humidity_avg_pct,
        narrative=narrative,
    )
