"""Tests for workflow domain models."""

import pytest

from playfile_core.workflows import (
    AgentInvocation,
    AgentStep,
    FilesConfig,
    StepValidation,
    Task,
    ValidationCommand,
    Workflow,
)


class TestFilesConfig:
    def test_files_config_creation(self):
        config = FilesConfig(read=["**/*.py"], write=["src/**/*.py"])
        assert config.read == ["**/*.py"]
        assert config.write == ["src/**/*.py"]

    def test_files_config_defaults(self):
        config = FilesConfig()
        assert config.read == []
        assert config.write == []

    def test_files_config_immutable(self):
        config = FilesConfig(read=["*.py"])
        with pytest.raises(Exception):
            config.read = ["*.js"]


class TestAgentInvocation:
    def test_agent_invocation_creation(self):
        invocation = AgentInvocation(
            use="fe-impl",
            with_params={"prompt": "Build the UI"},
        )
        assert invocation.use == "fe-impl"
        assert invocation.with_params == {"prompt": "Build the UI"}

    def test_agent_invocation_defaults(self):
        invocation = AgentInvocation(use="be-impl")
        assert invocation.with_params == {}

    def test_agent_invocation_empty_use(self):
        with pytest.raises(ValueError, match="use.*cannot be empty"):
            AgentInvocation(use="")

    def test_agent_invocation_immutable(self):
        invocation = AgentInvocation(use="fe-impl")
        with pytest.raises(Exception):
            invocation.use = "be-impl"


class TestValidationCommand:
    def test_validation_command_creation(self):
        cmd = ValidationCommand(command="pytest", description="Run tests")
        assert cmd.command == "pytest"
        assert cmd.description == "Run tests"

    def test_validation_command_no_description(self):
        cmd = ValidationCommand(command="pytest")
        assert cmd.command == "pytest"
        assert cmd.description is None

    def test_validation_command_empty_command(self):
        with pytest.raises(ValueError, match="command cannot be empty"):
            ValidationCommand(command="")

    def test_validation_command_immutable(self):
        cmd = ValidationCommand(command="pytest")
        with pytest.raises(Exception):
            cmd.command = "ruff"


class TestStepValidation:
    def test_step_validation_defaults(self):
        validation = StepValidation()
        assert validation.pre_command is None
        assert validation.post_command is None
        assert validation.post_commands == []
        assert validation.max_retries == 0
        assert validation.continue_on_failure is False

    def test_step_validation_with_pre_command(self):
        validation = StepValidation(pre_command="uv sync")
        assert validation.pre_command == "uv sync"

    def test_step_validation_with_post_command(self):
        validation = StepValidation(post_command="pytest", max_retries=2)
        assert validation.post_command == "pytest"
        assert validation.max_retries == 2

    def test_step_validation_with_post_commands(self):
        cmds = [
            ValidationCommand(command="ruff check", description="Lint"),
            ValidationCommand(command="pytest", description="Test"),
        ]
        validation = StepValidation(post_commands=cmds, max_retries=3)
        assert len(validation.post_commands) == 2
        assert validation.max_retries == 3

    def test_step_validation_both_post_command_and_commands(self):
        cmds = [ValidationCommand(command="pytest")]
        with pytest.raises(ValueError, match="Cannot specify both"):
            StepValidation(post_command="pytest", post_commands=cmds)

    def test_step_validation_negative_retries(self):
        with pytest.raises(ValueError, match="max_retries must be >= 0"):
            StepValidation(max_retries=-1)

    def test_step_validation_continue_on_failure(self):
        validation = StepValidation(
            post_command="pytest",
            max_retries=2,
            continue_on_failure=True,
        )
        assert validation.continue_on_failure is True

    def test_get_post_commands_from_single(self):
        validation = StepValidation(post_command="pytest tests/")
        cmds = validation.get_post_commands()
        assert len(cmds) == 1
        assert cmds[0].command == "pytest tests/"
        assert cmds[0].description is None

    def test_get_post_commands_from_list(self):
        cmds = [
            ValidationCommand(command="ruff check", description="Lint"),
            ValidationCommand(command="pytest", description="Test"),
        ]
        validation = StepValidation(post_commands=cmds)
        result = validation.get_post_commands()
        assert len(result) == 2
        assert result[0].command == "ruff check"
        assert result[1].command == "pytest"

    def test_get_post_commands_empty(self):
        validation = StepValidation()
        cmds = validation.get_post_commands()
        assert cmds == []

    def test_step_validation_immutable(self):
        validation = StepValidation(max_retries=2)
        with pytest.raises(Exception):
            validation.max_retries = 3


class TestAgentStep:
    def test_agent_step_creation(self):
        invocation = AgentInvocation(use="fe-impl", with_params={"prompt": "test"})
        step = AgentStep(agent=invocation)
        assert step.agent == invocation
        assert step.validate is None

    def test_agent_step_with_validation(self):
        invocation = AgentInvocation(use="coder")
        validation = StepValidation(post_command="pytest", max_retries=2)
        step = AgentStep(agent=invocation, validate=validation)
        assert step.agent == invocation
        assert step.validate == validation

    def test_agent_step_immutable(self):
        invocation = AgentInvocation(use="fe-impl")
        step = AgentStep(agent=invocation)
        with pytest.raises(Exception):
            step.agent = None


class TestTask:
    def test_task_creation_minimal(self):
        task = Task(id="test-task", description="Test description")
        assert task.id == "test-task"
        assert task.description == "Test description"
        assert task.working_dir == "."
        assert task.files is None
        assert task.steps == []

    def test_task_creation_full(self):
        files = FilesConfig(read=["**/*"], write=["src/**/*"])
        invocation = AgentInvocation(use="fe-impl", with_params={"prompt": "test"})
        step = AgentStep(agent=invocation)

        task = Task(
            id="implement-feature",
            description="Implement new feature",
            working_dir="/app",
            files=files,
            steps=[step],
        )

        assert task.id == "implement-feature"
        assert task.description == "Implement new feature"
        assert task.working_dir == "/app"
        assert task.files == files
        assert len(task.steps) == 1

    def test_task_empty_id(self):
        with pytest.raises(ValueError, match="id cannot be empty"):
            Task(id="", description="Test")

    def test_task_empty_description(self):
        with pytest.raises(ValueError, match="description cannot be empty"):
            Task(id="test", description="")

    def test_task_immutable(self):
        task = Task(id="test", description="Test")
        with pytest.raises(Exception):
            task.id = "new-id"


class TestWorkflow:
    def test_workflow_creation_minimal(self):
        workflow = Workflow(version=1)
        assert workflow.version == 1
        assert workflow.imports == []
        assert workflow.tasks == []

    def test_workflow_creation_full(self):
        task1 = Task(id="task1", description="Task 1")
        task2 = Task(id="task2", description="Task 2")

        workflow = Workflow(
            version=1,
            imports=["./tools.yaml", "./agents.yaml"],
            tasks=[task1, task2],
        )

        assert workflow.version == 1
        assert workflow.imports == ["./tools.yaml", "./agents.yaml"]
        assert len(workflow.tasks) == 2

    def test_workflow_invalid_version(self):
        with pytest.raises(ValueError, match="Version must be >= 1"):
            Workflow(version=0)

    def test_workflow_duplicate_task_ids(self):
        task1 = Task(id="same-id", description="Task 1")
        task2 = Task(id="same-id", description="Task 2")

        with pytest.raises(ValueError, match="Duplicate task IDs"):
            Workflow(version=1, tasks=[task1, task2])

    def test_workflow_get_task_exists(self):
        task = Task(id="test", description="Test")
        workflow = Workflow(version=1, tasks=[task])
        assert workflow.get_task("test") == task

    def test_workflow_get_task_not_exists(self):
        workflow = Workflow(version=1)
        assert workflow.get_task("nonexistent") is None

    def test_workflow_immutable(self):
        workflow = Workflow(version=1)
        with pytest.raises(Exception):
            workflow.version = 2
