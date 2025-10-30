"""Project package."""

__version__ = "0.1.0"


def greet(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: The name to greet

    Returns:
        A greeting message
    """
    return f"Hello, {name}!"
