import logging

from app.repositories.weather_reading_repository import WeatherReadingRepository

logger = logging.getLogger(__name__)


def check_supabase_connection(repository: WeatherReadingRepository | None = None) -> bool:
    try:
        repository = repository or WeatherReadingRepository()
        repository.ping()
        return True
    except Exception:
        # Boundary check: any downstream failure (auth, DNS, network, bad
        # credentials) means the same thing here - Supabase is unreachable.
        logger.exception("Supabase connectivity check failed")
        return False
