"""Tests for task runner."""

import tempfile
from pathlib import Path

from playfile_core import YamlAgentConfig
from playfile_core.workflows.files_config import FilesConfig
from playfile_core.workflows.task import Task

from playfile_cli.task_runner import TaskRunner


class TestTaskRunner:
    def test_collect_files_with_glob(self):
        """Test file collection with glob patterns."""
        # Create temp directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files
            (tmppath / "test1.py").write_text("# test 1")
            (tmppath / "test2.py").write_text("# test 2")
            (tmppath / "test.txt").write_text("text file")
            (tmppath / "subdir").mkdir()
            (tmppath / "subdir" / "test3.py").write_text("# test 3")

            # Create task with files config
            task = Task(
                id="test",
                description="Test",
                working_dir=str(tmppath),
                files=FilesConfig(read=["*.py", "subdir/*.py"]),
            )

            # Create minimal config
            config = YamlAgentConfig(version=1)
            runner = TaskRunner(config)

            # Collect files
            files = runner._collect_files(task)

            # Verify files collected
            assert files is not None
            assert len(files) == 3

            # Check filenames (paths will be absolute)
            filenames = [Path(f).name for f in files]
            assert "test1.py" in filenames
            assert "test2.py" in filenames
            assert "test3.py" in filenames
            assert "test.txt" not in filenames  # Not matched by pattern

    def test_collect_files_no_config(self):
        """Test file collection with no files config."""
        task = Task(id="test", description="Test", working_dir=".")

        config = YamlAgentConfig(version=1)
        runner = TaskRunner(config)

        files = runner._collect_files(task)

        assert files is None

    def test_collect_files_empty_patterns(self):
        """Test file collection with empty patterns."""
        task = Task(
            id="test",
            description="Test",
            working_dir=".",
            files=FilesConfig(read=[]),
        )

        config = YamlAgentConfig(version=1)
        runner = TaskRunner(config)

        files = runner._collect_files(task)

        assert files is None
