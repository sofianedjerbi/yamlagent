"""Tests for the main application."""

import pytest
from calculator_3d.main import create_app


@pytest.fixture
def app():
    """Create application fixture."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client fixture."""
    return app.test_client()


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "calculator-3d"


def test_index_route(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"3D Calculator" in response.data
