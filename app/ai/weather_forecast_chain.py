from functools import lru_cache

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.ai.prompts.weather_forecast_prompt import WEATHER_FORECAST_PROMPT
from app.config.settings import get_settings
from app.models.weather_statistics import WeatherStatistics


class NarrativeOutput(BaseModel):
    narrative: str


@lru_cache
def _get_chat_model() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(model=settings.forecast_model_name, api_key=settings.openai_api_key)


def _format_temperature(value: float | None) -> str:
    return f"{value:.1f}°C" if value is not None else "not available"


def _format_percentage(value: float | None) -> str:
    return f"{value:.0f}%" if value is not None else "not available"


def _format_precipitation(value: float | None) -> str:
    return f"{value:.1f} mm" if value is not None else "not available"


def generate_narrative(statistics: WeatherStatistics, llm: ChatOpenAI | None = None) -> str:
    llm = llm or _get_chat_model()
    chain = WEATHER_FORECAST_PROMPT | llm.with_structured_output(NarrativeOutput)

    result = chain.invoke(
        {
            "city": statistics.city,
            "date_label": f"{statistics.month:02d}/{statistics.day:02d}",
            "years_analyzed": statistics.years_analyzed,
            "temperature_avg": _format_temperature(statistics.temperature_avg_c),
            "temperature_max_avg": _format_temperature(statistics.temperature_max_avg_c),
            "temperature_min_avg": _format_temperature(statistics.temperature_min_avg_c),
            "precipitation_chance": _format_percentage(statistics.precipitation_chance_pct),
            "precipitation_avg": _format_precipitation(statistics.precipitation_avg_mm),
            "humidity_avg": _format_percentage(statistics.humidity_avg_pct),
        }
    )
    return result.narrative
