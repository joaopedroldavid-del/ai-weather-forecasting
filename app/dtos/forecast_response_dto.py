from pydantic import BaseModel


class ForecastConditionsDTO(BaseModel):
    temperature_max: float | None
    temperature_min: float | None
    temperature_avg: float | None
    wind_speed: float | None
    forecast: str
    precipitation: float | None


class ForecastResponseDTO(BaseModel):
    location: str
    date: str
    forecast: ForecastConditionsDTO
    narrative: str
