from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherStatistics:
    city: str
    month: int
    day: int
    years_analyzed: int
    temperature_avg_c: float | None
    temperature_max_avg_c: float | None
    temperature_min_avg_c: float | None
    precipitation_chance_pct: float | None
    precipitation_avg_mm: float | None
    humidity_avg_pct: float | None
