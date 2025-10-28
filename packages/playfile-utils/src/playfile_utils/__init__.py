"""Utilities"""

import json


def format_output(data: dict[str, str]) -> str:
    """Format data as JSON"""
    return json.dumps(data, indent=2)
