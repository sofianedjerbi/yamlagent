"""Custom exceptions for playfile-core."""

from __future__ import annotations


class YamlAgentError(Exception):
    """Base exception for all playfile errors."""


class ParseError(YamlAgentError):
    """Raised when YAML parsing fails."""


class ValidationError(YamlAgentError):
    """Raised when configuration validation fails."""
