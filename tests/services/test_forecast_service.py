from datetime import date

from app.models.weather_statistics import WeatherStatistics
from app.services import forecast_service


def _stats(**overrides):
    defaults = dict(
        city="São Paulo",
        month=7,
        day=15,
        years_analyzed=4,
        temperature_avg_c=22.0,
        temperature_max_avg_c=27.0,
        temperature_min_avg_c=17.0,
        precipitation_chance_pct=25.0,
        precipitation_avg_mm=3.5,
        humidity_avg_pct=70.0,
    )
    return WeatherStatistics(**{**defaults, **overrides})


def test_generate_forecast_assembles_dto_from_stats_and_narrative(monkeypatch):
    monkeypatch.setattr(forecast_service.weather_statistics_service, "compute_statistics", lambda *a, **k: _stats())
    monkeypatch.setattr(forecast_service, "generate_narrative", lambda stats: "Expect mild, mostly dry weather.")

    result = forecast_service.generate_forecast("São Paulo", date(2026, 7, 15))

    assert result.city == "São Paulo"
    assert result.target_date == date(2026, 7, 15)
    assert result.years_analyzed == 4
    assert result.confidence == "medium"
    assert result.temperature_avg_c == 22.0
    assert result.narrative == "Expect mild, mostly dry weather."


def test_confidence_level_buckets_by_sample_size():
    assert forecast_service._confidence_level(0) == "low"
    assert forecast_service._confidence_level(2) == "low"
    assert forecast_service._confidence_level(3) == "medium"
    assert forecast_service._confidence_level(5) == "medium"
    assert forecast_service._confidence_level(6) == "high"
