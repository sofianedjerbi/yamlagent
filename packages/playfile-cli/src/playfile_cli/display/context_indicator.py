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
            Formatted string like "[8%]" showing context usage (0% = free, 100% = full)
        """
        if not self._last_usage:
            # Show 0% if no usage data yet
            return "[green][0%][/green]"

        # Get total input tokens from usage
        # Note: cache_read_tokens are reused from cache, not new context consumption
        # Only count new input tokens and cache creation tokens as actual context usage
        input_tokens = self._last_usage.get("input_tokens", 0)
        cache_creation_tokens = self._last_usage.get("cache_creation_input_tokens", 0)

        # Total actual new context = new input + cache creation (not cache reads)
        total_input_tokens = input_tokens + cache_creation_tokens

        # Calculate percentage used (0% = all free, 100% = all used)
        pct_used = (total_input_tokens / self._max_tokens) * 100

        # Color code based on context usage
        if pct_used < 50:
            color = "green"
        elif pct_used < 75:
            color = "yellow"
        elif pct_used < 90:
            color = "red"
        else:
            color = "red bold"

        # Format: [8%] - percentage of context used (always show even if 0%)
        return f"[{color}][{pct_used:.0f}%][/{color}]"
