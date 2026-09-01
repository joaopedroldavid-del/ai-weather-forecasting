from dataclasses import dataclass


@dataclass(frozen=True)
class DailyWeatherSummary:
    year: int
    temperature_avg_c: float | None
    temperature_max_c: float | None
    temperature_min_c: float | None
    precipitation_total_mm: float | None
    humidity_avg_pct: float | None
