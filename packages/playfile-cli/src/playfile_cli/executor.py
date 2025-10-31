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
        request_summary: bool = False,
        next_agent_role: str | None = None,
    ) -> str | None:
        """Execute an agent with a prompt and optional file context.

        Args:
            agent: Agent configuration
            prompt: Prompt text
            working_dir: Working directory for execution
            files: List of file paths to include in context (optional)
            request_summary: Whether to request a summary after execution

        Returns:
            Agent response text (or summary if request_summary=True)
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
                    # Update context usage if available
                    if hasattr(message, 'usage') and message.usage:
                        self._context_indicator.update_usage(message.usage)

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

            # Request summary if needed
            if request_summary and response_text:
                self._console.print("\n[dim]Requesting summary from agent...[/dim]")
                summary = await self._request_summary(client, agent, next_agent_role)
                return summary

            return response_text

    async def _request_summary(
        self, client: ClaudeSDKClient, agent: Agent, next_agent_role: str | None = None
    ) -> str:
        """Request a summary from the agent after task completion.

        Args:
            client: Active Claude SDK client
            agent: Agent that performed the work
            next_agent_role: Role of the next agent in the workflow

        Returns:
            Summary text
        """
        if next_agent_role:
            summary_prompt = (
                f"Create a concise summary (2-4 sentences) specifically for the next agent: {next_agent_role}. "
                f"Include only the information they need to continue the work effectively. "
                f"What decisions did you make? What files did you create/modify? What should they know?"
            )
        else:
            summary_prompt = (
                "Create a concise summary (2-4 sentences) of the work you just completed. "
                "Include: what was done, key decisions made, and any important context "
                "for the next agent. Be specific and factual."
            )

        await client.query(summary_prompt)

        summary_text = ""
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        summary_text += block.text
            elif isinstance(message, ResultMessage):
                break

        self._console.print(f"[dim]Summary: {summary_text[:150]}...[/dim]\n")
        return summary_text
