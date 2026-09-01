from app.ai.weather_forecast_chain import (
    NarrativeOutput,
    _format_percentage,
    _format_precipitation,
    _format_temperature,
    _format_wind_speed,
    generate_narrative,
)
from app.models.weather_statistics import WeatherStatistics
from tests.mocks.chat_model_mock import FakeChatModel


def test_format_temperature_handles_value_and_none():
    assert _format_temperature(22.456) == "22.5°C"
    assert _format_temperature(None) == "not available"


def test_format_percentage_handles_value_and_none():
    assert _format_percentage(33.4) == "33%"
    assert _format_percentage(None) == "not available"


def test_format_precipitation_handles_value_and_none():
    assert _format_precipitation(4.26) == "4.3 mm"
    assert _format_precipitation(None) == "not available"


def test_format_wind_speed_converts_ms_to_kmh_and_handles_none():
    assert _format_wind_speed(5.0) == "18 km/h"
    assert _format_wind_speed(None) == "not available"


def test_generate_narrative_returns_llm_output():
    fake_llm = FakeChatModel(structured_output=NarrativeOutput(narrative="Mocked narrative."))
    stats = WeatherStatistics(
        city="São Paulo",
        month=7,
        day=15,
        years_analyzed=4,
        years=[2020, 2021, 2022, 2023],
        temperature_avg_c=22.0,
        temperature_max_avg_c=27.0,
        temperature_min_avg_c=17.0,
        precipitation_chance_pct=25.0,
        precipitation_avg_mm=3.5,
        humidity_avg_pct=70.0,
        wind_speed_avg_ms=5.0,
    )

    result = generate_narrative(stats, "cloudy", llm=fake_llm)

    assert result == "Mocked narrative."
    assert fake_llm.captured_schema is NarrativeOutput
