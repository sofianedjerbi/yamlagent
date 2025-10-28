"""Configuration loader - finds and loads playfile.yaml from project root."""

from __future__ import annotations

from pathlib import Path

from playfile_core import YamlAgentConfig, YamlAgentConfigParser
from playfile_core.exceptions import ParseError


class ConfigLoader:
    """Loads configuration from default or specified location."""

    DEFAULT_CONFIG_NAME = "playfile.yaml"

    def __init__(self, parser: YamlAgentConfigParser | None = None) -> None:
        """Initialize config loader.

        Args:
            parser: Config parser instance (optional, creates default if not provided)
        """
        self._parser = parser or YamlAgentConfigParser()

    def load(self, config_path: str | Path | None = None) -> YamlAgentConfig:
        """Load configuration from file.

        Args:
            config_path: Path to config file (optional, searches for default if not provided)

        Returns:
            Loaded configuration

        Raises:
            ParseError: If config file not found or invalid
        """
        if config_path:
            return self._parser.parse_file(config_path)

        # Search for default config
        config_file = self._find_config()
        if not config_file:
            msg = (
                f"Configuration file '{self.DEFAULT_CONFIG_NAME}' not found. "
                f"Searched in current directory and up to git root."
            )
            raise ParseError(msg)

        return self._parser.parse_file(config_file)

    def _find_config(self) -> Path | None:
        """Find playfile.yaml in current directory or up to git root.

        Returns:
            Path to config file or None if not found
        """
        current = Path.cwd()

        # Search upwards until we find playfile.yaml or reach git root
        while current != current.parent:
            config_path = current / self.DEFAULT_CONFIG_NAME
            if config_path.exists():
                return config_path

            # Stop at git root
            if (current / ".git").exists():
                # Check one more time at git root
                config_path = current / self.DEFAULT_CONFIG_NAME
                if config_path.exists():
                    return config_path
                break

            current = current.parent

        return None
