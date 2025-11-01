"""Tests for FastAPI endpoints."""

import pytest


def test_home_endpoint_returns_200(client):
    """Test that home endpoint returns successful response."""
    response = client.get("/")
    assert response.status_code == 200


def test_home_endpoint_returns_html(client):
    """Test that home endpoint returns HTML content."""
    response = client.get("/")
    assert "text/html" in response.headers["content-type"]


def test_home_page_contains_calculator(client):
    """Test that home page contains calculator elements."""
    response = client.get("/")
    content = response.text

    assert "Calc3D" in content
    assert "calculator" in content.lower()
    assert "display" in content.lower()


def test_health_endpoint_returns_200(client):
    """Test that health check endpoint is accessible."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_json(client):
    """Test that health endpoint returns JSON response."""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"


def test_health_endpoint_contains_status(client):
    """Test that health endpoint returns expected status."""
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "healthy"
    assert data["app"] == "calc3d"
    assert "version" in data


def test_static_files_accessible(client):
    """Test that static files are served correctly."""
    response = client.get("/static/js/calculator.js")
    assert response.status_code == 200


def test_nonexistent_endpoint_returns_404(client):
    """Test that nonexistent endpoints return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
