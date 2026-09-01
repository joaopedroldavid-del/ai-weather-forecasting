from datetime import date
from unittest.mock import MagicMock

import pytest

from app.models.weather_statistics import WeatherStatistics
from app.services import forecast_service
from app.services.exceptions import InsufficientHistoricalDataError


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
        wind_speed_avg_ms=5.0,
    )
    return WeatherStatistics(**{**defaults, **overrides})


def _fake_repository(cities=("São Paulo",)):
    repository = MagicMock()
    repository.list_cities.return_value = list(cities)
    return repository


def test_generate_forecast_assembles_dto_from_stats_and_narrative(monkeypatch):
    monkeypatch.setattr(forecast_service.weather_statistics_service, "compute_statistics", lambda *a, **k: _stats())
    monkeypatch.setattr(
        forecast_service, "generate_narrative", lambda stats, condition: "Expect mild, mostly dry weather."
    )

    result = forecast_service.generate_forecast("São Paulo", date(2026, 7, 15), repository=_fake_repository())

    assert result.city == "São Paulo"
    assert result.target_date == date(2026, 7, 15)
    assert result.years_analyzed == 4
    assert result.confidence == "medium"
    assert result.temperature_avg_c == 22.0
    assert result.wind_speed_kmh == pytest.approx(18.0)
    assert result.condition == "cloudy"
    assert result.narrative == "Expect mild, mostly dry weather."


def test_generate_forecast_uses_exact_match_without_fetching_city_list(monkeypatch):
    monkeypatch.setattr(forecast_service.weather_statistics_service, "compute_statistics", lambda *a, **k: _stats())
    monkeypatch.setattr(forecast_service, "generate_narrative", lambda stats, condition: "narrative")
    repository = _fake_repository()

    forecast_service.generate_forecast("São Paulo", date(2026, 7, 15), repository=repository)

    repository.list_cities.assert_not_called()


def test_generate_forecast_falls_back_to_resolved_city_name_on_mismatch(monkeypatch):
    calls = []

    def fake_compute_statistics(city, month, day, repository=None):
        calls.append(city)
        if city == "sao paulo":
            raise InsufficientHistoricalDataError("no exact match")
        return _stats()

    monkeypatch.setattr(forecast_service.weather_statistics_service, "compute_statistics", fake_compute_statistics)
    monkeypatch.setattr(forecast_service, "generate_narrative", lambda stats, condition: "narrative")
    repository = _fake_repository(cities=["São Paulo"])

    result = forecast_service.generate_forecast("sao paulo", date(2026, 7, 15), repository=repository)

    assert calls == ["sao paulo", "São Paulo"]
    assert result.city == "São Paulo"


def test_generate_forecast_reraises_insufficient_data_when_city_matches_exactly(monkeypatch):
    def fake_compute_statistics(city, month, day, repository=None):
        raise InsufficientHistoricalDataError("no data for this date")

    monkeypatch.setattr(forecast_service.weather_statistics_service, "compute_statistics", fake_compute_statistics)
    repository = _fake_repository(cities=["São Paulo"])

    with pytest.raises(InsufficientHistoricalDataError):
        forecast_service.generate_forecast("São Paulo", date(2026, 12, 25), repository=repository)


def test_generate_forecast_raises_unsupported_location_when_no_match(monkeypatch):
    def fake_compute_statistics(city, month, day, repository=None):
        raise InsufficientHistoricalDataError("no data")

    monkeypatch.setattr(forecast_service.weather_statistics_service, "compute_statistics", fake_compute_statistics)
    repository = _fake_repository(cities=["São Paulo"])

    with pytest.raises(forecast_service.UnsupportedLocationError):
        forecast_service.generate_forecast("Atlantis", date(2026, 7, 15), repository=repository)


def test_confidence_level_buckets_by_sample_size():
    assert forecast_service._confidence_level(0) == "low"
    assert forecast_service._confidence_level(2) == "low"
    assert forecast_service._confidence_level(3) == "medium"
    assert forecast_service._confidence_level(5) == "medium"
    assert forecast_service._confidence_level(6) == "high"


def test_classify_condition_thresholds():
    assert forecast_service._classify_condition(None) == "unknown"
    assert forecast_service._classify_condition(10.0) == "sunny"
    assert forecast_service._classify_condition(20.0) == "cloudy"
    assert forecast_service._classify_condition(49.9) == "cloudy"
    assert forecast_service._classify_condition(50.0) == "rain"
    assert forecast_service._classify_condition(80.0) == "rain"


def test_resolve_city_matches_case_and_accent_insensitively():
    repository = _fake_repository(cities=["São Paulo"])

    assert forecast_service._resolve_city("sao paulo", repository) == "São Paulo"
    assert forecast_service._resolve_city("SÃO PAULO", repository) == "São Paulo"


def test_resolve_city_raises_for_unknown_location():
    repository = _fake_repository(cities=["São Paulo"])

    with pytest.raises(forecast_service.UnsupportedLocationError):
        forecast_service._resolve_city("Atlantis", repository)
