from pydantic import BaseModel


class ForecastRequestDTO(BaseModel):
    location: str
    date: str
