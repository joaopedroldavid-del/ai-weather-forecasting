from unittest.mock import MagicMock

from app.services import health_service
from app.services.health_service import check_supabase_connection


def test_check_supabase_connection_returns_true_when_ping_succeeds():
    repository = MagicMock()
    repository.ping.return_value = None

    assert check_supabase_connection(repository) is True


def test_check_supabase_connection_returns_false_when_ping_raises():
    repository = MagicMock()
    repository.ping.side_effect = Exception("connection refused")

    assert check_supabase_connection(repository) is False


def test_check_supabase_connection_returns_false_when_repository_construction_fails(monkeypatch):
    def _raise():
        raise Exception("supabase_url is required")

    monkeypatch.setattr(health_service, "WeatherReadingRepository", _raise)

    assert check_supabase_connection() is False
