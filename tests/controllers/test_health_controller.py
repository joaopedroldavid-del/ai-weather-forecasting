from fastapi.testclient import TestClient

from app.controllers import health_controller
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_returns_200_when_supabase_up(monkeypatch):
    monkeypatch.setattr(health_controller, "check_supabase_connection", lambda: True)

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "dependencies": {"supabase": "up"}}


def test_readiness_returns_503_when_supabase_down(monkeypatch):
    monkeypatch.setattr(health_controller, "check_supabase_connection", lambda: False)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "dependencies": {"supabase": "down"}}
