import unicodedata
from datetime import date

from app.ai.weather_forecast_chain import generate_narrative
from app.dtos.weather_forecast_dto import WeatherForecastDTO
from app.repositories.weather_reading_repository import WeatherReadingRepository
from app.services import weather_statistics_service
from app.services.exceptions import InsufficientHistoricalDataError, UnsupportedLocationError
from app.utils.unit_conversion import ms_to_kmh

CONFIDENCE_LOW_MAX_YEARS = 2
CONFIDENCE_MEDIUM_MAX_YEARS = 5

CONDITION_RAIN_THRESHOLD_PCT = 50.0
CONDITION_CLOUDY_THRESHOLD_PCT = 20.0


def _confidence_level(years_analyzed: int) -> str:
    if years_analyzed <= CONFIDENCE_LOW_MAX_YEARS:
        return "low"
    if years_analyzed <= CONFIDENCE_MEDIUM_MAX_YEARS:
        return "medium"
    return "high"


def _classify_condition(precipitation_chance_pct: float | None) -> str:
    if precipitation_chance_pct is None:
        return "unknown"
    if precipitation_chance_pct >= CONDITION_RAIN_THRESHOLD_PCT:
        return "rain"
    if precipitation_chance_pct >= CONDITION_CLOUDY_THRESHOLD_PCT:
        return "cloudy"
    return "sunny"


def _normalize_city_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return without_accents.strip().casefold()


def _resolve_city(location: str, repository: WeatherReadingRepository) -> str:
    target = _normalize_city_name(location)
    for known_city in repository.list_cities():
        if _normalize_city_name(known_city) == target:
            return known_city
    raise UnsupportedLocationError(f"Unsupported location: {location}")


def generate_forecast(
    city: str, target_date: date, repository: WeatherReadingRepository | None = None
) -> WeatherForecastDTO:
    repository = repository or WeatherReadingRepository()

    try:
        # Happy path: the given name matches a stored city exactly, so this
        # is the only query needed - no need to pull the full city list.
        stats = weather_statistics_service.compute_statistics(
            city, target_date.month, target_date.day, repository=repository
        )
    except InsufficientHistoricalDataError:
        resolved_city = _resolve_city(city, repository)
        if resolved_city == city:
            raise  # Known city, genuinely no data for this date - not a name mismatch.
        stats = weather_statistics_service.compute_statistics(
            resolved_city, target_date.month, target_date.day, repository=repository
        )

    condition = _classify_condition(stats.precipitation_chance_pct)
    narrative = generate_narrative(stats, condition)

    wind_speed_kmh = ms_to_kmh(stats.wind_speed_avg_ms) if stats.wind_speed_avg_ms is not None else None

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
        wind_speed_kmh=wind_speed_kmh,
        condition=condition,
        narrative=narrative,
    )
