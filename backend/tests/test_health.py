import pytest
from unittest.mock import patch
from app.main import app


def test_health_endpoint_healthy(client):
    """Test /api/health when database is healthy."""
    with patch("app.main.check_db_health", return_value=(True, "Database connection healthy.")):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "CloudModX"
        assert data["database_connected"] is True
        assert data["database_status"] == "connected"


def test_health_endpoint_degraded(client):
    """Test /api/health when database is unavailable."""
    with patch("app.main.check_db_health", return_value=(False, "Connection refused")):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database_connected"] is False
        assert data["database_status"] == "disconnected"
        assert "unavailable" in data["details"]


def test_root_endpoint(client):
    """Test root endpoint metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "CloudModX" in data["message"]
    assert data["health"] == "/api/health"
