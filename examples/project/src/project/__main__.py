"""Main entry point for the project package."""

from project import greet


def main() -> None:
    """Run the main application."""
    message = greet()
    print(message)


if __name__ == "__main__":
    main()
