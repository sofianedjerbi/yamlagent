"""Example tests for the project package."""

from project import greet


def test_greet_default():
    """Test greet function with default argument."""
    result = greet()
    assert result == "Hello, World!"


def test_greet_custom_name():
    """Test greet function with custom name."""
    result = greet("Alice")
    assert result == "Hello, Alice!"
