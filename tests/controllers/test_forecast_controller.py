from datetime import date

from fastapi.testclient import TestClient

from app.dtos.weather_forecast_dto import WeatherForecastDTO
from app.main import app
from app.services import forecast_service
from app.services.exceptions import InsufficientHistoricalDataError, UnsupportedLocationError

client = TestClient(app)


def _forecast_dto(**overrides):
    defaults = dict(
        city="São Paulo",
        target_date=date(2026, 9, 2),
        years_analyzed=4,
        confidence="medium",
        temperature_avg_c=22.0,
        temperature_max_avg_c=27.0,
        temperature_min_avg_c=17.0,
        precipitation_chance_pct=25.0,
        precipitation_avg_mm=3.5,
        humidity_avg_pct=70.0,
        wind_speed_kmh=18.0,
        condition="cloudy",
        narrative="Expect mild, mostly dry weather.",
    )
    return WeatherForecastDTO(**{**defaults, **overrides})


def test_create_forecast_returns_expected_shape(monkeypatch):
    monkeypatch.setattr(forecast_service, "generate_forecast", lambda city, target_date: _forecast_dto())

    response = client.post("/forecast", json={"location": "São Paulo", "date": "09-02-2026"})

    assert response.status_code == 200
    assert response.json() == {
        "location": "São Paulo",
        "date": "09-02-2026",
        "forecast": {
            "temperature_max": 27.0,
            "temperature_min": 17.0,
            "temperature_avg": 22.0,
            "wind_speed": 18.0,
            "forecast": "cloudy",
            "precipitation": 3.5,
        },
        "narrative": "Expect mild, mostly dry weather.",
    }


def test_create_forecast_returns_400_for_invalid_date_format():
    response = client.post("/forecast", json={"location": "São Paulo", "date": "2026-09-02"})

    assert response.status_code == 400


def test_create_forecast_returns_404_for_unsupported_location(monkeypatch):
    def _raise(city, target_date):
        raise UnsupportedLocationError("nope")

    monkeypatch.setattr(forecast_service, "generate_forecast", _raise)

    response = client.post("/forecast", json={"location": "Atlantis", "date": "09-02-2026"})

    assert response.status_code == 404


def test_create_forecast_returns_404_for_no_historical_data(monkeypatch):
    def _raise(city, target_date):
        raise InsufficientHistoricalDataError("nope")

    monkeypatch.setattr(forecast_service, "generate_forecast", _raise)

    response = client.post("/forecast", json={"location": "São Paulo", "date": "09-02-2026"})

    assert response.status_code == 404


def test_create_forecast_returns_500_and_hides_details_on_unexpected_error(monkeypatch):
    def _raise(city, target_date):
        raise RuntimeError("db connection string leaked here")

    monkeypatch.setattr(forecast_service, "generate_forecast", _raise)

    response = client.post("/forecast", json={"location": "São Paulo", "date": "09-02-2026"})

    assert response.status_code == 500
    assert "db connection string" not in response.text
