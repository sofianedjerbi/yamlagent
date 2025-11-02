"""Tool usage and result formatting for terminal display."""

# ruff: noqa: E501  # Allow long lines for Rich markup formatting

from __future__ import annotations

from typing import Any

from claude_agent_sdk import ToolResultBlock, ToolUseBlock
from rich.console import Console

from playfile_cli.display.diff_formatter import DiffFormatter


class ToolFormatter:
    """Formats tool usage and results for rich terminal display."""

    def __init__(
        self,
        console: Console | None = None,
    ) -> None:
        """Initialize formatter.

        Args:
            console: Rich console for output
        """
        self._console = console or Console()
        self._diff_formatter = DiffFormatter(self._console)

    def format_tool_id(self, tool_id: str) -> str:
        """Format tool ID for display.

        Args:
            tool_id: Full tool use ID

        Returns:
            Formatted ID string for display
        """
        return f"[dim italic](id:{tool_id[:8]})[/dim italic]"

    def print_tool_usage(self, block: ToolUseBlock) -> None:
        """Print detailed tool usage information with maximum traceability.

        Args:
            block: ToolUseBlock with tool name and input
        """
        tool_name = block.name
        tool_input = block.input
        tool_id_fmt = self.format_tool_id(block.id)

        # Format based on tool type with maximum detail
        if tool_name == "Read":
            self._print_read_tool(tool_input, tool_id_fmt)
        elif tool_name == "Write":
            self._print_write_tool(tool_input, tool_id_fmt)
        elif tool_name == "Edit":
            self._print_edit_tool(tool_input, tool_id_fmt)
        elif tool_name == "Glob":
            self._print_glob_tool(tool_input, tool_id_fmt)
        elif tool_name == "Grep":
            self._print_grep_tool(tool_input, tool_id_fmt)
        elif tool_name == "Bash":
            self._print_bash_tool(tool_input, tool_id_fmt)
        elif tool_name == "Task":
            self._print_task_tool(tool_input, tool_id_fmt)
        elif tool_name == "TodoWrite":
            self._print_todo_tool(tool_input, tool_id_fmt)
        elif tool_name == "NotebookEdit":
            self._print_notebook_tool(tool_input, tool_id_fmt)
        elif tool_name == "WebFetch":
            self._print_webfetch_tool(tool_input, tool_id_fmt)
        elif tool_name == "WebSearch":
            self._print_websearch_tool(tool_input, tool_id_fmt)
        elif tool_name == "BashOutput":
            self._print_bash_output_tool(tool_input, tool_id_fmt)
        elif tool_name == "KillShell":
            self._print_kill_shell_tool(tool_input, tool_id_fmt)
        elif tool_name == "ExitPlanMode":
            self._print_plan_tool(tool_input, tool_id_fmt)
        else:
            self._print_generic_tool(tool_name, tool_input, tool_id_fmt)

    def print_tool_result(self, block: ToolResultBlock) -> None:
        """Print tool execution results with detailed status.

        Args:
            block: ToolResultBlock with execution results
        """
        tool_id_fmt = self.format_tool_id(block.tool_use_id)
        is_error = block.is_error

        if is_error:
            # Show errors prominently
            error_content = ""
            if isinstance(block.content, str):
                error_content = block.content[:100]
            elif isinstance(block.content, list):
                error_content = str(block.content)[:100]
            self._console.print(
                f"[dim]   ❌ [red bold]Error:[/red bold] {error_content}... "
                f"{tool_id_fmt}[/dim]",
            )
        else:
            # Parse result content for specific tools
            result_summary = self._get_result_summary(block.content)
            if result_summary:
                self._console.print(
                    f"[dim]   ✓ {result_summary} {tool_id_fmt}[/dim]",
                )

    def _print_read_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print Read tool usage."""
        
        file_path = tool_input.get("file_path", "")
        offset = tool_input.get("offset")
        limit = tool_input.get("limit")
        range_info = ""
        if offset or limit:
            end = offset + limit if offset and limit else limit or "end"
            range_info = f" [lines {offset or 'start'}-{end}]"
        self._console.print(
            f"[dim][bold]Read:[/bold] [cyan]{file_path}[/cyan]"
            f"{range_info} {tool_id_fmt}[/dim]",
        )

    def _print_write_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print Write tool usage with diff if file exists."""
        
        file_path = tool_input.get("file_path", "")
        new_content = tool_input.get("content", "")
        content_length = len(new_content)

        # Check if file exists to show diff
        from pathlib import Path

        path = Path(file_path).resolve()
        if path.exists() and path.is_file():
            # File exists - show as edit with diff
            try:
                old_content = path.read_text(encoding="utf-8", errors="replace")
                old_len = len(old_content)

                # Only show diff if content is actually different
                if old_content != new_content:
                    self._console.print(
                        f"[dim][bold]Write:[/bold] [yellow]{file_path}[/yellow] "
                        f"[dim]({old_len}→{content_length} bytes)[/dim] {tool_id_fmt}[/dim]",
                    )
                    # Show diff
                    self._diff_formatter.print_compact_edit(file_path, old_content, new_content)
                else:
                    # Content is identical - no changes
                    self._console.print(
                        f"[dim][bold]Write:[/bold] [cyan]{file_path}[/cyan] "
                        f"[dim](no changes, {content_length} bytes)[/dim] {tool_id_fmt}[/dim]",
                    )
            except Exception as e:
                # Fallback if can't read file
                self._console.print(
                    f"[dim][bold]Write:[/bold] [green]{file_path}[/green] "
                    f"[dim]({content_length} bytes, error reading old: {e})[/dim] {tool_id_fmt}[/dim]",
                )
        else:
            # New file - show content
            self._console.print(
                f"[dim][bold]Write:[/bold] [green]{file_path}[/green] "
                f"[dim](new file, {content_length} bytes)[/dim] {tool_id_fmt}[/dim]",
            )
            # Show the content with syntax highlighting
            from rich.panel import Panel
            from rich.syntax import Syntax

            # Detect language from file extension
            file_ext = Path(file_path).suffix
            lang_map = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".jsx": "jsx",
                ".tsx": "tsx",
                ".html": "html",
                ".css": "css",
                ".json": "json",
                ".yaml": "yaml",
                ".yml": "yaml",
                ".md": "markdown",
                ".sh": "bash",
                ".sql": "sql",
                ".go": "go",
                ".rs": "rust",
                ".java": "java",
                ".cpp": "cpp",
                ".c": "c",
            }
            language = lang_map.get(file_ext, "text")

            # Limit display to reasonable length
            display_content = new_content
            if len(new_content) > 5000:
                lines = new_content.splitlines()
                if len(lines) > 100:
                    display_content = "\n".join(lines[:100]) + "\n\n... (truncated)"

            syntax = Syntax(
                display_content,
                language,
                line_numbers=True,
                word_wrap=False,
                theme="ansi_dark",
                background_color="default",
            )
            self._console.print(
                Panel(
                    syntax,
                    title=f"[bold green]New File: {file_path}[/bold green]",
                    border_style="green",
                    padding=(0, 1),
                )
            )

    def _print_edit_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print Edit tool usage with diff preview."""
        
        file_path = tool_input.get("file_path", "")
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        replace_all = tool_input.get("replace_all", False)

        mode = "replace all" if replace_all else "replace once"
        old_len = len(old_string)
        new_len = len(new_string)

        # Show brief header
        self._console.print(
            f"[dim][bold]Edit:[/bold] [yellow]{file_path}[/yellow] [dim]({mode}, {old_len}→{new_len} bytes)[/dim] {tool_id_fmt}[/dim]",
        )

        # Show the diff
        self._diff_formatter.print_compact_edit(file_path, old_string, new_string)

    def _print_glob_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print Glob tool usage."""
        
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", ".")
        self._console.print(
            f"[dim][bold]Glob:[/bold] [cyan]{pattern}[/cyan] in {path} {tool_id_fmt}[/dim]",
        )

    def _print_grep_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print Grep tool usage."""
        
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", ".")
        output_mode = tool_input.get("output_mode", "files_with_matches")
        case_insensitive = " [case-insensitive]" if tool_input.get("-i") else ""
        self._console.print(
            f"[dim][bold]Grep:[/bold] [cyan]'{pattern}'[/cyan] in {path} [dim](mode:{output_mode}{case_insensitive})[/dim] {tool_id_fmt}[/dim]",
        )

    def _print_bash_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print Bash tool usage."""
        
        command = tool_input.get("command", "")
        description = tool_input.get("description", "")
        timeout = tool_input.get("timeout", 120000)
        background = tool_input.get("run_in_background", False)

        display_cmd = command if len(command) <= 80 else command[:77] + "..."
        mode = " [background]" if background else ""
        desc = f" - {description}" if description else ""
        self._console.print(
            f"[dim][bold]Bash:[/bold] [magenta]{display_cmd}[/magenta]{mode} [dim](timeout:{timeout / 1000}s)[/dim]{desc} {tool_id_fmt}[/dim]",
        )

    def _print_task_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print Task (subagent) tool usage."""
        description = tool_input.get("description", "")
        prompt = tool_input.get("prompt", "")
        subagent_type = tool_input.get("subagent_type", "")

        
        prompt_preview = prompt[:60] + "..." if len(prompt) > 60 else prompt
        self._console.print(
            f"[dim][bold]Task:[/bold] [blue]{description}[/blue] [dim](agent:{subagent_type})[/dim]\n   [dim italic]Prompt: {prompt_preview}[/dim italic] {tool_id_fmt}[/dim]",
        )

    def _print_todo_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print TodoWrite tool usage with todo list."""
        from rich.panel import Panel
        from rich.text import Text

        todos = tool_input.get("todos", [])
        pending = sum(1 for t in todos if t.get("status") == "pending")
        in_progress = sum(1 for t in todos if t.get("status") == "in_progress")
        completed = sum(1 for t in todos if t.get("status") == "completed")
        

        # Show header with counts
        self._console.print(
            f"[dim][bold]Todos:[/bold] {len(todos)} items [dim](✓{completed} ▶{in_progress} ○{pending})[/dim] {tool_id_fmt}[/dim]",
        )

        # Show todo list
        if todos:
            todo_text = Text()
            for i, todo in enumerate(todos, 1):
                status = todo.get("status", "pending")
                content = todo.get("content", "")
                active_form = todo.get("activeForm", content)

                # Status icon
                if status == "completed":
                    icon = "✓"
                    style = "green"
                    text = content
                elif status == "in_progress":
                    icon = "▶"
                    style = "yellow"
                    text = active_form
                else:
                    icon = "○"
                    style = "dim"
                    text = content

                todo_text.append(f"{i}. {icon} ", style=style)
                # Don't add newline after last item
                if i < len(todos):
                    todo_text.append(f"{text}\n", style=style if status != "pending" else "")
                else:
                    todo_text.append(f"{text}", style=style if status != "pending" else "")

            self._console.print(
                Panel(
                    todo_text,
                    border_style="blue",
                    padding=(0, 1),
                )
            )

    def _print_notebook_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print NotebookEdit tool usage."""
        notebook_path = tool_input.get("notebook_path", "")
        cell_id = tool_input.get("cell_id", "")
        edit_mode = tool_input.get("edit_mode", "replace")
        cell_type = tool_input.get("cell_type", "code")
        
        self._console.print(
            f"[dim][bold]Notebook:[/bold] [yellow]{notebook_path}[/yellow] [dim](cell:{cell_id[:8]}, {edit_mode}, {cell_type})[/dim] {tool_id_fmt}[/dim]",
        )

    def _print_webfetch_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print WebFetch tool usage."""
        url = tool_input.get("url", "")
        prompt = tool_input.get("prompt", "")[:40]
        
        self._console.print(
            f"[dim][bold]WebFetch:[/bold] [cyan]{url}[/cyan]\n   [dim italic]Query: {prompt}...[/dim italic] {tool_id_fmt}[/dim]",
        )

    def _print_websearch_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print WebSearch tool usage."""
        query = tool_input.get("query", "")
        allowed = tool_input.get("allowed_domains", [])
        blocked = tool_input.get("blocked_domains", [])
        filters = ""
        if allowed:
            filters = f" [allow:{','.join(allowed[:2])}]"
        if blocked:
            filters += f" [block:{','.join(blocked[:2])}]"
        
        self._console.print(
            f"[dim][bold]WebSearch:[/bold] [cyan]'{query}'[/cyan]{filters} {tool_id_fmt}[/dim]",
        )

    def _print_bash_output_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print BashOutput tool usage."""
        bash_id = tool_input.get("bash_id", "")
        filter_pattern = tool_input.get("filter")
        filter_info = f" [filter:{filter_pattern}]" if filter_pattern else ""
        
        self._console.print(
            f"[dim][bold]BashOutput:[/bold] shell:{bash_id}{filter_info} {tool_id_fmt}[/dim]",
        )

    def _print_kill_shell_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print KillShell tool usage."""
        shell_id = tool_input.get("shell_id", "")
        
        self._console.print(
            f"[dim][bold]KillShell:[/bold] shell:{shell_id} {tool_id_fmt}[/dim]",
        )

    def _print_plan_tool(self, tool_input: dict[str, Any], tool_id_fmt: str) -> None:
        """Print ExitPlanMode tool usage."""
        plan = tool_input.get("plan", "")[:80]
        
        self._console.print(
            f"[dim][bold]Plan:[/bold] {plan}... {tool_id_fmt}[/dim]",
        )

    def _print_generic_tool(
        self, tool_name: str, tool_input: dict[str, Any], tool_id_fmt: str
    ) -> None:
        """Print generic tool usage."""
        
        params = ", ".join(f"{k}={str(v)[:20]}" for k, v in tool_input.items() if k and v)
        self._console.print(
            f"[dim][bold]{tool_name}:[/bold] [dim]{params}[/dim] {tool_id_fmt}[/dim]",
        )

    def _get_result_summary(self, content: Any) -> str:
        """Extract summary from tool result content.

        Args:
            content: Tool result content

        Returns:
            Human-readable summary string
        """
        if isinstance(content, str):
            # Try to parse common result patterns
            if "matches" in content.lower():
                return f"[cyan]{content[:60]}[/cyan]"
            if "created" in content.lower() or "written" in content.lower():
                return f"[green]{content[:60]}[/green]"
            if "found" in content.lower():
                return f"[blue]{content[:60]}[/blue]"
            return ""

        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    # Check for specific result types
                    if "text" in item:
                        text = item["text"]
                        # Extract file count from Glob results
                        if "files" in text.lower() or "match" in text.lower():
                            return f"[cyan]{text[:60]}[/cyan]"
                        # Extract success messages
                        if "success" in text.lower() or "complete" in text.lower():
                            return f"[green]{text[:60]}[/green]"
                        # Show first meaningful line
                        if len(text) > 10:
                            return f"{text[:60]}..."

        return ""
