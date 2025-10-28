"""Agent executor - runs agents via Claude SDK."""

from __future__ import annotations

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
)
from playfile_core.agents.agent import Agent
from playfile_core.tools.agent_tools import AgentTools
from rich.console import Console

from playfile_cli.display import ContextIndicator, ToolFormatter
from playfile_cli.sdk_options import SdkOptionsBuilder


class AgentExecutor:
    """Executes agents using Claude SDK."""

    def __init__(
        self,
        tools: AgentTools | None = None,
        console: Console | None = None,
    ) -> None:
        """Initialize executor.

        Args:
            tools: Available tools configuration
            console: Rich console for output
        """
        self._tools = tools
        self._console = console or Console()
        self._context_indicator = ContextIndicator()
        self._tool_formatter = ToolFormatter(self._console, self._context_indicator)

    async def execute(
        self,
        agent: Agent,
        prompt: str,
        working_dir: str = ".",
        files: list[str] | None = None,
    ) -> str | None:
        """Execute an agent with a prompt and optional file context.

        Args:
            agent: Agent configuration
            prompt: Prompt text
            working_dir: Working directory for execution
            files: List of file paths to include in context (optional)

        Returns:
            Agent response text
        """
        # Build Claude SDK options
        options = SdkOptionsBuilder.build_options(agent, working_dir, files)

        # Execute with Claude SDK using streaming mode
        async with ClaudeSDKClient(options=options) as client:
            # Send prompt
            await client.query(prompt)

            # Stream response with live output following SDK best practices
            response_text = ""
            last_was_text = False

            async for message in client.receive_messages():
                # Handle AssistantMessage with proper type checking
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Show context indicator before text
                            ctx = self._context_indicator.get_indicator()
                            if ctx and response_text == "":
                                # Only show at start of response
                                self._console.print(f"{ctx} ", end="")
                            # Stream text content as it arrives
                            self._console.print(block.text, end="")
                            response_text += block.text
                            last_was_text = True
                        elif isinstance(block, ThinkingBlock):
                            # Show thinking blocks if present
                            thinking_preview = block.thinking[:100]
                            self._console.print(
                                f"\n[dim][Thinking: {thinking_preview}...][/dim]\n", end=""
                            )
                            last_was_text = False
                        elif isinstance(block, ToolUseBlock):
                            # Add newline if previous block was text
                            if last_was_text:
                                self._console.print()
                                last_was_text = False
                            # Show tool usage with details
                            self._tool_formatter.print_tool_usage(block)
                        elif isinstance(block, ToolResultBlock):
                            # Show tool results
                            self._tool_formatter.print_tool_result(block)

                # Check for completion
                elif isinstance(message, ResultMessage):
                    # Update context usage from result
                    if message.usage:
                        self._context_indicator.update_usage(message.usage)
                    break

            # Print newline at the end
            self._console.print()
            return response_text
