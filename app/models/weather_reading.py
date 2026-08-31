from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class WeatherReading:
    uf: str
    city: str
    observed_at: datetime
    precipitation_mm: float | None
    pressure_mb: float | None
    pressure_max_mb: float | None
    pressure_min_mb: float | None
    radiation_kj_m2: float | None
    temperature_c: float | None
    dew_point_c: float | None
    temperature_max_c: float | None
    temperature_min_c: float | None
    dew_point_max_c: float | None
    dew_point_min_c: float | None
    humidity_max_pct: float | None
    humidity_min_pct: float | None
    humidity_pct: float | None
    wind_direction_deg: float | None
    wind_gust_ms: float | None
    wind_speed_ms: float | None
