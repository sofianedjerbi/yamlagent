"""Task runner - executes workflow tasks."""

from __future__ import annotations

import asyncio
from typing import Any

from playfile_core import YamlAgentConfig
from playfile_core.workflows.task import Task
from rich.console import Console
from rich.panel import Panel

from playfile_cli.executor import AgentExecutor


class TaskRunner:
    """Executes workflow tasks with agent orchestration."""

    def __init__(self, config: YamlAgentConfig, console: Console | None = None) -> None:
        """Initialize task runner.

        Args:
            config: Loaded configuration
            console: Rich console for output (optional, creates default if not provided)
        """
        self._config = config
        self._console = console or Console()
        self._executor = AgentExecutor(config.tools, console)

    def run(self, task_id: str, inputs: dict[str, Any] | None = None) -> None:
        """Run a workflow task.

        Args:
            task_id: ID of task to run
            inputs: Input parameters for task (optional)

        Raises:
            ValueError: If task not found or no workflows defined
        """
        if not self._config.workflows:
            msg = "No workflows defined in configuration"
            raise ValueError(msg)

        task = self._config.workflows.get_task(task_id)
        if not task:
            available = [t.id for t in self._config.workflows.tasks]
            msg = f"Task '{task_id}' not found. Available tasks: {', '.join(available)}"
            raise ValueError(msg)

        self._execute_task(task, inputs or {})

    def _execute_task(self, task: Task, inputs: dict[str, Any]) -> None:
        """Execute a single task.

        Args:
            task: Task to execute
            inputs: Input parameters
        """
        # Display task header
        self._console.print()
        self._console.print(
            Panel.fit(
                f"[bold cyan]{task.description}[/bold cyan]\n"
                f"[dim]Task: {task.id}[/dim]",
                border_style="cyan",
            )
        )

        if not task.steps:
            self._console.print("[yellow]⚠ No steps defined for this task[/yellow]")
            return

        # Execute each step
        for i, step in enumerate(task.steps, 1):
            agent_id = step.agent.use

            # Get agent from config
            if not self._config.agents:
                msg = "No agents defined in configuration"
                raise ValueError(msg)

            agent = self._config.agents.get_agent(agent_id)
            if not agent:
                msg = f"Agent '{agent_id}' not found in configuration"
                raise ValueError(msg)

            # Render prompt with inputs
            prompt = self._render_prompt(step.agent.with_params.get("prompt", ""), inputs)

            # Collect files from task configuration
            files = self._collect_files(task)

            # Display step header
            step_info = f"\n[bold cyan]→ Step {i}/{len(task.steps)}:[/bold cyan]"
            agent_info = f" {agent.role} ({agent.model})"
            self._console.print(step_info + agent_info)

            prompt_preview = prompt[:200] + ("..." if len(prompt) > 200 else "")
            self._console.print(f"[dim]Prompt: {prompt_preview}[/dim]")
            if files:
                self._console.print(f"[dim]Files: {len(files)} file(s)[/dim]\n")
            else:
                self._console.print()

            # Execute agent (response is streamed live by executor)
            try:
                asyncio.run(
                    self._executor.execute(agent, prompt, task.working_dir, files)
                )
                # Response already printed by executor during streaming

            except Exception as e:
                self._console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
                raise

        self._console.print("\n[bold green]✓ Task completed successfully[/bold green]\n")

    def _collect_files(self, task: Task) -> list[str] | None:
        """Collect files from task configuration.

        Args:
            task: Task configuration

        Returns:
            List of file paths or None
        """
        if not task.files or not task.files.read:
            return None

        import glob
        from pathlib import Path

        files = []
        base_path = Path(task.working_dir)

        # Expand glob patterns from files.read
        for pattern in task.files.read:
            # Make pattern relative to working dir
            full_pattern = str(base_path / pattern)

            # Expand glob
            matched = glob.glob(full_pattern, recursive=True)

            # Filter out directories, keep only files
            for path in matched:
                if Path(path).is_file():
                    files.append(path)

        return files if files else None

    def _render_prompt(self, prompt_template: str, inputs: dict[str, Any]) -> str:
        """Render prompt template with input variables.

        Args:
            prompt_template: Template string with {{ inputs.var }} placeholders
            inputs: Input variables

        Returns:
            Rendered prompt
        """
        rendered = prompt_template

        # Simple template rendering (can be enhanced with Jinja2 later)
        for key, value in inputs.items():
            placeholder = f"{{{{ inputs.{key} }}}}"
            rendered = rendered.replace(placeholder, str(value))

        return rendered
