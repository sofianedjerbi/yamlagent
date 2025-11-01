"""Pytest configuration and fixtures for Calc3D tests."""

import pytest
from fastapi.testclient import TestClient

from calc3d.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_calculator_state():
    """Sample calculator state for testing."""
    return {
        "display": "0",
        "current_value": 0,
        "previous_value": None,
        "operation": None,
        "waiting_for_operand": False,
        "should_reset_display": False,
    }
