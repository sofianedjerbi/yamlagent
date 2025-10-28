"""Tests for workflow domain models."""

import pytest

from playfile_core.workflows import (
    AgentInvocation,
    AgentStep,
    FilesConfig,
    Task,
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


class TestAgentStep:
    def test_agent_step_creation(self):
        invocation = AgentInvocation(use="fe-impl", with_params={"prompt": "test"})
        step = AgentStep(agent=invocation)
        assert step.agent == invocation

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
