"""End-to-end test configuration and shared fixtures.

This module provides fixtures used across all e2e tests for ats-linter.
Every fixture is intentionally simple so that test intent remains clear.
"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ats_linter.cli import app


@pytest.fixture
def cli_runner() -> CliRunner:
    """Return a Typer CliRunner that invokes the real ats-linter CLI.

    Using the CliRunner keeps tests fast and hermetic while exercising
    the full application stack (file collection → AST parsing → linting).
    """
    return CliRunner()


@pytest.fixture
def run_linter(cli_runner: CliRunner):
    """Return a callable that invokes the linter and returns the result.

    The helper accepts any number of path arguments (files or directories)
    and optional extra flags, mirroring real CLI usage.

    Example::

        result = run_linter(str(some_file))
        assert result.exit_code == 0
    """

    def _run(*paths: str, extra_args: list[str] | None = None) -> object:
        args = list(paths) + (extra_args or [])
        return cli_runner.invoke(app, args)

    return _run


@pytest.fixture
def write_test_file(tmp_path: Path):
    """Return a factory that writes a Python test file and returns its path.

    Keeping file creation centralised here means individual tests only
    need to specify the *content* they care about.

    Example::

        test_file = write_test_file("test_example.py", content)
        assert test_file.exists()
    """

    def _write(filename: str, content: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path

    return _write
