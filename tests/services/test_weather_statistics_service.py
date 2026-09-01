from datetime import datetime, timezone

import pytest

from app.services.exceptions import InsufficientHistoricalDataError
from app.services.weather_statistics_service import _summarize_day, compute_statistics
from tests.factories.weather_reading_factory import build_weather_reading


def _reading(year, hour, **overrides):
    return build_weather_reading(observed_at=datetime(year, 7, 15, hour, tzinfo=timezone.utc), **overrides)


def test_summarize_day_averages_and_ignores_none_values():
    readings = [
        _reading(2020, 0, temperature_c=20.0, precipitation_mm=0.0, humidity_pct=70.0),
        _reading(2020, 12, temperature_c=30.0, precipitation_mm=None, humidity_pct=80.0),
    ]

    summary = _summarize_day(2020, readings)

    assert summary.year == 2020
    assert summary.temperature_avg_c == 25.0
    assert summary.temperature_max_c == 30.0
    assert summary.temperature_min_c == 20.0
    assert summary.precipitation_total_mm == 0.0
    assert summary.humidity_avg_pct == 75.0


def test_summarize_day_returns_none_when_all_values_missing():
    readings = [_reading(2020, 0, temperature_c=None, precipitation_mm=None, humidity_pct=None)]

    summary = _summarize_day(2020, readings)

    assert summary.temperature_avg_c is None
    assert summary.temperature_max_c is None
    assert summary.temperature_min_c is None
    assert summary.precipitation_total_mm is None
    assert summary.humidity_avg_pct is None


def test_compute_statistics_aggregates_across_years():
    repository = _FakeRepository(
        readings=[
            _reading(2020, 0, temperature_c=20.0, precipitation_mm=0.0, humidity_pct=70.0),
            _reading(2021, 0, temperature_c=24.0, precipitation_mm=5.0, humidity_pct=80.0),
            _reading(2022, 0, temperature_c=22.0, precipitation_mm=0.0, humidity_pct=75.0),
        ]
    )

    stats = compute_statistics("São Paulo", 7, 15, repository=repository)

    assert stats.city == "São Paulo"
    assert stats.years_analyzed == 3
    assert stats.temperature_avg_c == pytest.approx(22.0)
    assert stats.precipitation_avg_mm == pytest.approx(5.0 / 3)
    # 1 of 3 years had measurable rain
    assert stats.precipitation_chance_pct == pytest.approx(100 / 3)


def test_compute_statistics_raises_when_no_historical_data():
    repository = _FakeRepository(readings=[])

    with pytest.raises(InsufficientHistoricalDataError):
        compute_statistics("São Paulo", 7, 15, repository=repository)


class _FakeRepository:
    def __init__(self, readings):
        self._readings = readings

    def find_by_city_and_day_of_month(self, city, month, day):
        return self._readings
