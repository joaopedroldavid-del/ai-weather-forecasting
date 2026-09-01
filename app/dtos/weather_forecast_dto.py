from datetime import date

from pydantic import BaseModel


class WeatherForecastDTO(BaseModel):
    city: str
    target_date: date
    years_analyzed: int
    confidence: str
    temperature_avg_c: float | None
    temperature_max_avg_c: float | None
    temperature_min_avg_c: float | None
    precipitation_chance_pct: float | None
    precipitation_avg_mm: float | None
    humidity_avg_pct: float | None
    wind_speed_kmh: float | None
    condition: str
    narrative: str
