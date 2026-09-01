from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Weather Forecasting API"
    environment: str = "development"

    supabase_url: str = ""
    supabase_service_role_key: str = ""

    logfire_token: str = ""

    openai_api_key: str = ""
    forecast_model_name: str = "gpt-4o-mini"


@lru_cache
def get_settings() -> Settings:
    return Settings()
