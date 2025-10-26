"""Tests for workflow YAML parser."""

import tempfile
from pathlib import Path

import pytest

from yamlagent_core.exceptions import ParseError, ValidationError
from yamlagent_core.workflows.parser import (
    AgentStepParser,
    FilesConfigParser,
    TaskParser,
    WorkflowParser,
    YAMLWorkflowLoader,
)


class TestYAMLWorkflowLoader:
    def test_load_valid_yaml(self):
        content = "version: 1\ntasks:\n  - id: test\n    description: Test"
        loader = YAMLWorkflowLoader()
        result = loader.load(content)
        assert result["version"] == 1

    def test_load_invalid_yaml(self):
        content = "version: 1\n  invalid: indent"
        loader = YAMLWorkflowLoader()
        with pytest.raises(ParseError, match="Invalid YAML"):
            loader.load(content)

    def test_load_non_dict_yaml(self):
        content = "- item1\n- item2"
        loader = YAMLWorkflowLoader()
        with pytest.raises(ParseError, match="must be a dictionary"):
            loader.load(content)


class TestFilesConfigParser:
    def test_parse_full(self):
        data = {"read": ["**/*"], "write": ["src/**/*"]}
        parser = FilesConfigParser()
        config = parser.parse(data)
        assert config.read == ["**/*"]
        assert config.write == ["src/**/*"]

    def test_parse_empty(self):
        data = {}
        parser = FilesConfigParser()
        config = parser.parse(data)
        assert config.read == []
        assert config.write == []


class TestAgentStepParser:
    def test_parse_valid_step(self):
        data = {
            "agent": {
                "use": "fe-impl",
                "with": {"prompt": "Build UI"},
            }
        }
        parser = AgentStepParser()
        step = parser.parse(data)
        assert step.agent.use == "fe-impl"
        assert step.agent.with_params == {"prompt": "Build UI"}

    def test_parse_step_without_with(self):
        data = {"agent": {"use": "be-impl"}}
        parser = AgentStepParser()
        step = parser.parse(data)
        assert step.agent.use == "be-impl"
        assert step.agent.with_params == {}

    def test_parse_step_missing_agent(self):
        data = {"other": "field"}
        parser = AgentStepParser()
        with pytest.raises(ValidationError, match="Invalid agent step"):
            parser.parse(data)

    def test_parse_step_missing_use(self):
        data = {"agent": {"with": {"prompt": "test"}}}
        parser = AgentStepParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)


class TestTaskParser:
    def test_parse_minimal(self):
        data = {"id": "test-task", "description": "Test description"}
        parser = TaskParser()
        task = parser.parse(data)
        assert task.id == "test-task"
        assert task.description == "Test description"
        assert task.working_dir == "."
        assert task.files is None
        assert task.steps == []

    def test_parse_full(self):
        data = {
            "id": "implement-feature",
            "description": "Implement new feature",
            "working_dir": "/app",
            "files": {"read": ["**/*"], "write": ["src/**/*"]},
            "steps": [
                {"agent": {"use": "fe-impl", "with": {"prompt": "Build UI"}}},
                {"agent": {"use": "be-impl", "with": {"prompt": "Build API"}}},
            ],
        }
        parser = TaskParser()
        task = parser.parse(data)
        assert task.id == "implement-feature"
        assert task.working_dir == "/app"
        assert task.files is not None
        assert len(task.steps) == 2

    def test_parse_missing_id(self):
        data = {"description": "Test"}
        parser = TaskParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)

    def test_parse_missing_description(self):
        data = {"id": "test"}
        parser = TaskParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)


class TestWorkflowParser:
    def test_parse_complete_workflow(self):
        content = """
version: 1

imports:
  - ./tools.yaml
  - ./agents.yaml

tasks:
  - id: implement-feature
    description: "Implement a new feature"
    working_dir: "."
    files:
      read:
        - "**/*"
      write:
        - "**/*"
    steps:
      - agent:
          use: fe-impl
          with:
            prompt: |
              Build the frontend for:
              {{ inputs.prompt }}

      - agent:
          use: be-impl
          with:
            prompt: |
              Build the backend for:
              {{ inputs.prompt }}

  - id: clean-code
    description: "Clean code refactor"
    working_dir: "."
    files:
      read:
        - "**/*"
      write:
        - "**/*"
    steps:
      - agent:
          use: be-impl
          with:
            prompt: |
              Apply strict clean code
"""
        parser = WorkflowParser()
        workflow = parser.parse(content)

        assert workflow.version == 1
        assert workflow.imports == ["./tools.yaml", "./agents.yaml"]
        assert len(workflow.tasks) == 2

        # Check first task
        task1 = workflow.get_task("implement-feature")
        assert task1 is not None
        assert task1.description == "Implement a new feature"
        assert len(task1.steps) == 2
        assert task1.steps[0].agent.use == "fe-impl"
        assert task1.steps[1].agent.use == "be-impl"

        # Check second task
        task2 = workflow.get_task("clean-code")
        assert task2 is not None
        assert len(task2.steps) == 1

    def test_parse_minimal_workflow(self):
        content = "version: 1"
        parser = WorkflowParser()
        workflow = parser.parse(content)
        assert workflow.version == 1
        assert workflow.tasks == []

    def test_parse_invalid_yaml(self):
        content = "version: 1\n  invalid: indent"
        parser = WorkflowParser()
        with pytest.raises(ParseError):
            parser.parse(content)

    def test_parse_file_success(self):
        content = """
version: 1
tasks:
  - id: test-task
    description: "Test"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            parser = WorkflowParser()
            workflow = parser.parse_file(temp_path)
            assert workflow.version == 1
            assert len(workflow.tasks) == 1
        finally:
            Path(temp_path).unlink()

    def test_parse_file_not_found(self):
        parser = WorkflowParser()
        with pytest.raises(ParseError, match="File not found"):
            parser.parse_file("/nonexistent/file.yaml")

    def test_parse_duplicate_task_ids(self):
        content = """
version: 1
tasks:
  - id: same-id
    description: "Task 1"
  - id: same-id
    description: "Task 2"
"""
        parser = WorkflowParser()
        with pytest.raises(ValidationError, match="Duplicate task IDs"):
            parser.parse(content)

    def test_parse_with_imports(self):
        # Create a temporary import file
        import_content = """
tasks:
  - id: imported-task
    description: "Imported task"
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, dir="/tmp"
        ) as import_file:
            import_file.write(import_content)
            import_path = Path(import_file.name)

        # Create main workflow that imports the file
        main_content = f"""
version: 1
imports:
  - {import_path.name}
tasks:
  - id: main-task
    description: "Main task"
"""

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False, dir="/tmp"
            ) as main_file:
                main_file.write(main_content)
                main_path = Path(main_file.name)

            parser = WorkflowParser()
            workflow = parser.parse_file(main_path)

            # Should have both main and imported tasks
            assert len(workflow.tasks) == 2
            assert workflow.get_task("main-task") is not None
            assert workflow.get_task("imported-task") is not None
        finally:
            import_path.unlink()
            main_path.unlink()
