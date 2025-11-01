"""Task runner - executes workflow tasks."""

from __future__ import annotations

import asyncio
import subprocess
from typing import Any

from playfile_core import YamlAgentConfig
from playfile_core.workflows.task import Task
from rich.console import Console
from rich.panel import Panel

from playfile_cli.artifacts import ArtifactCollector, StepArtifact
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

        # Initialize artifact collector for this task
        artifacts = ArtifactCollector()

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

            # Render prompt with inputs and artifacts
            base_prompt = self._render_prompt(step.agent.with_params.get("prompt", ""), inputs)

            # Add working directory context
            working_dir_context = f"WORKING DIRECTORY: {task.working_dir}\n\n"

            # Add project overview context if available
            project_context = self._get_project_context(task.working_dir)

            # Build full prompt with all context
            context_parts = [working_dir_context]

            if project_context:
                context_parts.append(f"{project_context}\n\n")

            # Get context from specified steps or all previous steps
            context_from = step.agent.context_from if step.agent.context_from else None
            if artifacts.has_artifacts():
                artifact_context = artifacts.get_context_for_next_step(context_from)
                if artifact_context:
                    context_parts.append(f"{artifact_context}\n\n")

            context_parts.append(base_prompt)
            prompt = "".join(context_parts)

            # Collect files from task configuration
            files = self._collect_files(task)

            # Display step header
            step_info = f"\n[bold cyan]→ Step {i}/{len(task.steps)}:[/bold cyan]"
            agent_info = f" [bold]{agent.id}[/bold] - {agent.role} ({agent.model})"
            self._console.print(step_info + agent_info)

            prompt_preview = base_prompt[:200] + ("..." if len(base_prompt) > 200 else "")
            self._console.print(f"[dim]Prompt: {prompt_preview}[/dim]")

            # Show context information
            if artifacts.has_artifacts():
                if context_from:
                    # Show which specific steps are being used
                    self._console.print(f"[dim]Context from: {', '.join(context_from)}[/dim]")
                else:
                    # Show all previous steps
                    num_artifacts = len(artifacts._artifacts)
                    self._console.print(f"[dim]Context: {num_artifacts} previous step(s)[/dim]")

            if files:
                self._console.print(f"[dim]Files: {len(files)} file(s)[/dim]\n")
            else:
                self._console.print()

            # Execute step with retry logic and capture artifact
            try:
                has_more_steps = i < len(task.steps)

                # Determine next agent's role and task name if there are more steps
                next_agent_role = None
                next_task_name = None
                if has_more_steps:
                    next_step = task.steps[i]  # i is 1-indexed, so this gives us the next step
                    next_agent_id = next_step.agent.use
                    next_agent = self._config.agents.get_agent(next_agent_id)
                    if next_agent:
                        next_agent_role = next_agent.role
                    # Get next step's name if available
                    if next_step.name:
                        next_task_name = next_step.name

                summary = self._execute_step_with_retry(
                    step, agent, prompt, task.working_dir, files,
                    request_summary=has_more_steps, next_agent_role=next_agent_role,
                    next_task_name=next_task_name
                )

                # Add artifact if we got a summary
                if summary and has_more_steps:
                    artifact = StepArtifact(
                        step_number=i,
                        step_id=step.id,
                        agent_id=agent.id,
                        agent_role=agent.role,
                        summary=summary,
                    )
                    artifacts.add_artifact(artifact)

            except Exception as e:
                # If continue_on_failure is True, log error and continue
                if step.validate and step.validate.continue_on_failure:
                    msg = f"\n[bold yellow]⚠ Step failed but continuing:[/bold yellow] {e}\n"
                    self._console.print(msg)
                else:
                    self._console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
                    raise

        self._console.print("\n[bold green]✓ Task completed successfully[/bold green]\n")

    def _execute_step_with_retry(
        self,
        step: Any,
        agent: Any,
        prompt: str,
        working_dir: str,
        files: list[str] | None,
        request_summary: bool = False,
        next_agent_role: str | None = None,
        next_task_name: str | None = None,
    ) -> str | None:
        """Execute a step with retry logic and validation.

        Args:
            step: Agent step configuration
            agent: Agent to execute
            prompt: Rendered prompt
            working_dir: Working directory for execution
            files: List of files to provide
            request_summary: Whether to request a summary after execution
            next_agent_role: Role of the next agent in the workflow
            next_task_name: Name of the next task/step

        Returns:
            Summary text if request_summary=True, otherwise None

        Raises:
            Exception: If step fails after all retries
        """
        validation = step.validate
        max_attempts = 1 + (validation.max_retries if validation else 0)

        # Run pre-command if specified
        if validation and validation.pre_command:
            self._console.print(f"[dim]→ Running pre-validation: {validation.pre_command}[/dim]")
            success, output = self._run_command(validation.pre_command, working_dir)
            if not success:
                msg = f"Pre-validation command failed: {validation.pre_command}"
                raise RuntimeError(msg)
            self._console.print("[dim]✓ Pre-validation passed[/dim]\n")

        # Execute agent with retry loop
        validation_failures = []

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                retry_msg = (
                    f"\n[bold yellow]↻ Retry attempt "
                    f"{attempt - 1}/{validation.max_retries}[/bold yellow]\n"
                )
                self._console.print(retry_msg)

                # Add validation failure context to prompt for retry
                if validation_failures:
                    failure_context = self._format_validation_failures(validation_failures)
                    retry_prompt = f"{failure_context}\n\n{prompt}"
                else:
                    retry_prompt = prompt
            else:
                retry_prompt = prompt

            # Execute agent
            try:
                result = asyncio.run(
                    self._executor.execute(
                        agent, retry_prompt, working_dir, files,
                        request_summary=request_summary, next_agent_role=next_agent_role,
                        next_task_name=next_task_name
                    )
                )
                # Response already printed by executor during streaming

            except Exception as e:
                # Agent execution failed
                if attempt == max_attempts:
                    # No more retries
                    raise
                self._console.print(f"\n[yellow]⚠ Agent execution failed: {e}[/yellow]")
                continue

            # Run post-validation commands if specified
            if validation:
                post_commands = validation.get_commands()
                if post_commands:
                    check_msg = (
                        f"\n[dim]→ Running validation "
                        f"({len(post_commands)} check(s))...[/dim]"
                    )
                    self._console.print(check_msg)

                    all_passed = True
                    validation_failures = []  # Reset failures for this attempt

                    for cmd in post_commands:
                        desc = cmd.description or cmd.command
                        self._console.print(f"[dim]  • {desc}[/dim]")

                        success, output = self._run_command(cmd.command, working_dir)
                        if not success:
                            all_passed = False
                            validation_failures.append({
                                "command": cmd.command,
                                "description": desc,
                                "output": output,
                            })

                            if attempt == max_attempts:
                                # No more retries
                                msg = f"Validation failed: {cmd.command}"
                                raise RuntimeError(msg)
                            self._console.print(f"[yellow]    ✗ Validation failed: {desc}[/yellow]")
                            # Show truncated output
                            if output:
                                preview = output[:200] + ("..." if len(output) > 200 else "")
                                self._console.print(f"[dim]    Output: {preview}[/dim]")
                            break
                        else:
                            self._console.print("[dim]    ✓ Passed[/dim]")

                    if all_passed:
                        self._console.print("[dim]✓ All validations passed[/dim]")
                        return result  # Success!
                    else:
                        # Validation failed, retry with context
                        continue
                else:
                    # No validation commands, consider success
                    return result
            else:
                # No validation configured, consider success
                return result

        # Should never reach here, but just in case
        msg = "Step failed after all retry attempts"
        raise RuntimeError(msg)

    def _format_validation_failures(self, failures: list[dict]) -> str:
        """Format validation failures for agent context.

        Args:
            failures: List of failure dicts with command, description, output

        Returns:
            Formatted failure message
        """
        lines = ["## VALIDATION FAILURES - Please fix these issues:\n"]

        for i, failure in enumerate(failures, 1):
            lines.append(f"{i}. {failure['description']}")
            lines.append(f"   Command: {failure['command']}")
            if failure['output']:
                lines.append(f"   Output:\n   {failure['output']}\n")
            else:
                lines.append("")

        return "\n".join(lines)

    def _run_command(self, command: str, working_dir: str) -> tuple[bool, str]:
        """Run a shell command and return success status with output.

        Args:
            command: Command to execute
            working_dir: Working directory

        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            # Combine stdout and stderr
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr

            return (result.returncode == 0, output.strip())
        except subprocess.TimeoutExpired:
            self._console.print("[red]Command timeout (5 minutes)[/red]")
            return (False, "Command timeout (5 minutes)")
        except Exception as e:
            self._console.print(f"[red]Command execution error: {e}[/red]")
            return (False, f"Command execution error: {e}")

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

    def _get_project_context(self, working_dir: str) -> str | None:
        """Get project context from .play/project/ files if available.

        Args:
            working_dir: Working directory

        Returns:
            Project context string or None
        """
        from pathlib import Path

        project_dir = Path(working_dir) / ".play" / "project"
        overview_file = project_dir / "overview.md"
        guidelines_file = project_dir / "guidelines.md"

        context_parts = []

        # Read overview (short project purpose)
        if overview_file.exists():
            try:
                content = overview_file.read_text()
                context_parts.append(f"# PROJECT OVERVIEW\n\n{content}")
            except Exception:
                pass

        # Read guidelines (best practices and conventions)
        if guidelines_file.exists():
            try:
                content = guidelines_file.read_text()
                context_parts.append(f"# PROJECT GUIDELINES\n\n{content}")
            except Exception:
                pass

        if context_parts:
            return "\n\n".join(context_parts)

        return None

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
