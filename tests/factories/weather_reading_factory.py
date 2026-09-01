from datetime import datetime, timezone

from app.models.weather_reading import WeatherReading
from app.repositories.weather_reading_repository import (
    COL_CIDADE,
    COL_DATA,
    COL_HORA_UTC,
    COL_ORVALHO,
    COL_ORVALHO_MAX,
    COL_ORVALHO_MIN,
    COL_PRECIPITACAO,
    COL_PRESSAO,
    COL_PRESSAO_MAX,
    COL_PRESSAO_MIN,
    COL_RADIACAO,
    COL_TEMPERATURA,
    COL_TEMPERATURA_MAX,
    COL_TEMPERATURA_MIN,
    COL_UF,
    COL_UMIDADE,
    COL_UMIDADE_MAX,
    COL_UMIDADE_MIN,
    COL_VENTO_DIRECAO,
    COL_VENTO_RAJADA,
    COL_VENTO_VELOCIDADE,
)

DEFAULT_RAW_ROW = {
    COL_UF: "SP",
    COL_CIDADE: "São Paulo",
    COL_DATA: "2020/01/01",
    COL_HORA_UTC: "0000 UTC",
    COL_PRECIPITACAO: "0",
    COL_PRESSAO: "922,3",
    COL_PRESSAO_MAX: "922,3",
    COL_PRESSAO_MIN: "921,2",
    COL_RADIACAO: "",
    COL_TEMPERATURA: "23,3",
    COL_ORVALHO: "18,1",
    COL_TEMPERATURA_MAX: "24,1",
    COL_TEMPERATURA_MIN: "23,2",
    COL_ORVALHO_MAX: "18,3",
    COL_ORVALHO_MIN: "17",
    COL_UMIDADE_MAX: "73",
    COL_UMIDADE_MIN: "65",
    COL_UMIDADE: "73",
    COL_VENTO_DIRECAO: "71",
    COL_VENTO_RAJADA: "4,3",
    COL_VENTO_VELOCIDADE: "1,8",
}


def build_raw_row(**overrides: str) -> dict:
    return {**DEFAULT_RAW_ROW, **overrides}


DEFAULT_WEATHER_READING_KWARGS = dict(
    uf="SP",
    city="São Paulo",
    observed_at=datetime(2020, 1, 1, 12, tzinfo=timezone.utc),
    precipitation_mm=0.0,
    pressure_mb=922.3,
    pressure_max_mb=922.3,
    pressure_min_mb=921.2,
    radiation_kj_m2=None,
    temperature_c=23.3,
    dew_point_c=18.1,
    temperature_max_c=24.1,
    temperature_min_c=23.2,
    dew_point_max_c=18.3,
    dew_point_min_c=17.0,
    humidity_max_pct=73.0,
    humidity_min_pct=65.0,
    humidity_pct=73.0,
    wind_direction_deg=71.0,
    wind_gust_ms=4.3,
    wind_speed_ms=1.8,
)


def build_weather_reading(**overrides) -> WeatherReading:
    return WeatherReading(**{**DEFAULT_WEATHER_READING_KWARGS, **overrides})
