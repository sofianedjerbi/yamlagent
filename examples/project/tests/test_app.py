"""Basic tests for the calculator application."""

import pytest
from calculator_3d.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_page(client):
    """Test that the index page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"3D Calculator" in response.data


def test_calculate_addition(client):
    """Test addition calculation."""
    response = client.post(
        "/api/calculate",
        json={"expression": "2+2"},
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == 4


def test_calculate_multiplication(client):
    """Test multiplication calculation."""
    response = client.post(
        "/api/calculate",
        json={"expression": "5*3"},
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == 15


def test_calculate_power(client):
    """Test power calculation."""
    response = client.post(
        "/api/calculate",
        json={"expression": "2^3"},
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == 8


def test_calculate_invalid_expression(client):
    """Test that invalid expressions return an error."""
    response = client.post(
        "/api/calculate",
        json={"expression": "invalid"},
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
