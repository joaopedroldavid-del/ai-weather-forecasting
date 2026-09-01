from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Weather Forecasting API"

    cors_allowed_origins: str = "http://localhost:4200"

    supabase_url: str = ""
    supabase_service_role_key: str = ""

    openai_api_key: str = ""
    forecast_model_name: str = "gpt-4o-mini"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
