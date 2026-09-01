from collections import defaultdict
from statistics import mean

from app.models.daily_weather_summary import DailyWeatherSummary
from app.models.weather_reading import WeatherReading
from app.models.weather_statistics import WeatherStatistics
from app.repositories.weather_reading_repository import WeatherReadingRepository
from app.services.exceptions import InsufficientHistoricalDataError


def _mean(values: list[float]) -> float | None:
    return mean(values) if values else None


def _summarize_day(year: int, readings: list[WeatherReading]) -> DailyWeatherSummary:
    temperatures = [r.temperature_c for r in readings if r.temperature_c is not None]
    precipitations = [r.precipitation_mm for r in readings if r.precipitation_mm is not None]
    humidities = [r.humidity_pct for r in readings if r.humidity_pct is not None]

    return DailyWeatherSummary(
        year=year,
        temperature_avg_c=_mean(temperatures),
        temperature_max_c=max(temperatures) if temperatures else None,
        temperature_min_c=min(temperatures) if temperatures else None,
        precipitation_total_mm=sum(precipitations) if precipitations else None,
        humidity_avg_pct=_mean(humidities),
    )


def compute_statistics(
    city: str, month: int, day: int, repository: WeatherReadingRepository | None = None
) -> WeatherStatistics:
    repository = repository or WeatherReadingRepository()
    readings = repository.find_by_city_and_day_of_month(city, month, day)

    if not readings:
        raise InsufficientHistoricalDataError(
            f"No historical data for {city} on {month:02d}/{day:02d}"
        )

    readings_by_year = defaultdict(list)
    for reading in readings:
        readings_by_year[reading.observed_at.year].append(reading)

    summaries = [_summarize_day(year, year_readings) for year, year_readings in readings_by_year.items()]

    precipitation_totals = [s.precipitation_total_mm for s in summaries if s.precipitation_total_mm is not None]
    precipitation_chance_pct = (
        sum(1 for total in precipitation_totals if total > 0) / len(precipitation_totals) * 100
        if precipitation_totals
        else None
    )

    return WeatherStatistics(
        city=city,
        month=month,
        day=day,
        years_analyzed=len(summaries),
        temperature_avg_c=_mean([s.temperature_avg_c for s in summaries if s.temperature_avg_c is not None]),
        temperature_max_avg_c=_mean([s.temperature_max_c for s in summaries if s.temperature_max_c is not None]),
        temperature_min_avg_c=_mean([s.temperature_min_c for s in summaries if s.temperature_min_c is not None]),
        precipitation_chance_pct=precipitation_chance_pct,
        precipitation_avg_mm=_mean(precipitation_totals),
        humidity_avg_pct=_mean([s.humidity_avg_pct for s in summaries if s.humidity_avg_pct is not None]),
    )
