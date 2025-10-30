"""Tests for the main module."""

from myproject.__main__ import main


def test_main(capsys):
    """Test the main function."""
    main()
    captured = capsys.readouterr()
    assert "Hello from myproject!" in captured.out
