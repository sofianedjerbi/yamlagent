"""Context usage indicator for terminal display."""

from __future__ import annotations


class ContextIndicator:
    """Formats context usage percentage in a compact, beautiful way."""

    def __init__(self, max_tokens: int = 200000) -> None:
        """Initialize context indicator.

        Args:
            max_tokens: Maximum context window size
        """
        self._max_tokens = max_tokens
        self._last_usage: dict[str, int] | None = None

    def update_usage(self, usage: dict[str, int] | None) -> None:
        """Update the current usage information.

        Args:
            usage: Usage dict from ResultMessage
        """
        self._last_usage = usage

    def get_indicator(self) -> str:
        """Get a compact context indicator string.

        Returns:
            Formatted string like "[92%]" with color coding
        """
        if not self._last_usage:
            return ""

        # Get input tokens from usage
        input_tokens = self._last_usage.get("input_tokens", 0)

        # Calculate percentage used
        pct_used = (input_tokens / self._max_tokens) * 100
        pct_left = 100 - pct_used

        # Color code based on remaining context
        if pct_left > 50:
            color = "green"
        elif pct_left > 25:
            color = "yellow"
        elif pct_left > 10:
            color = "red"
        else:
            color = "red bold"

        # Format: [92%] - percentage remaining
        return f"[{color}][{pct_left:.0f}%][/{color}]"
