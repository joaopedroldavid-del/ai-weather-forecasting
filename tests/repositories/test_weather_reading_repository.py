from datetime import date, datetime, timezone

import pytest

from app.repositories import weather_reading_repository as repo_module
from app.repositories.weather_reading_repository import (
    COL_CIDADE,
    WeatherReadingRepository,
    _parse_float,
    _parse_observed_at,
)
from tests.factories.weather_reading_factory import build_raw_row
from tests.mocks.supabase_client_mock import FakeSupabaseClient


def test_parse_observed_at_combines_date_and_hour_into_utc_datetime():
    result = _parse_observed_at("2020/01/01", "1300 UTC")

    assert result == datetime(2020, 1, 1, 13, tzinfo=timezone.utc)


def test_find_by_city_builds_expected_query_and_maps_rows(monkeypatch):
    monkeypatch.setattr(repo_module, "_parse_float", lambda raw: None)
    raw_row = build_raw_row()
    fake_client = FakeSupabaseClient(data=[raw_row])
    repository = WeatherReadingRepository(client=fake_client)

    results = repository.find_by_city("São Paulo", date(2020, 1, 1), date(2020, 1, 31))

    assert fake_client.table_name == "bdmep_forecast"
    assert ("eq", (COL_CIDADE, "São Paulo")) in fake_client.last_query_builder.calls
    assert len(results) == 1
    assert results[0].city == "São Paulo"
    assert results[0].uf == "SP"
    assert results[0].observed_at == datetime(2020, 1, 1, 0, tzinfo=timezone.utc)


def test_find_by_city_and_day_of_month_builds_like_pattern_query(monkeypatch):
    monkeypatch.setattr(repo_module, "_parse_float", lambda raw: None)
    raw_row = build_raw_row()
    fake_client = FakeSupabaseClient(data=[raw_row])
    repository = WeatherReadingRepository(client=fake_client)

    results = repository.find_by_city_and_day_of_month("São Paulo", 7, 15)

    assert ("eq", (COL_CIDADE, "São Paulo")) in fake_client.last_query_builder.calls
    assert ("like", ("Data", "%/07/15")) in fake_client.last_query_builder.calls
    assert len(results) == 1


def test_list_cities_returns_sorted_unique_cities():
    fake_client = FakeSupabaseClient(
        data=[
            build_raw_row(**{COL_CIDADE: "São Paulo"}),
            build_raw_row(**{COL_CIDADE: "Florianópolis"}),
            build_raw_row(**{COL_CIDADE: "São Paulo"}),
        ]
    )
    repository = WeatherReadingRepository(client=fake_client)

    result = repository.list_cities()

    assert result == ["Florianópolis", "São Paulo"]


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("922,3", 922.3),
        ("0", 0.0),
        ("", None),
        (None, None),
        (",8", 0.8),
        (",2", 0.2),
        ("abc", None),
    ],
)
def test_parse_float_handles_comma_decimals_and_blanks(raw, expected):
    assert _parse_float(raw) == expected
