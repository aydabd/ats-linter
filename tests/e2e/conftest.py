"""End-to-end test configuration and shared fixtures.

This module provides fixtures and helpers used across all e2e tests for ats-linter.

Structure
---------
Tests are split into focused files, one concern per file:

    test_e2e_compliant_schemas.py    — every valid ATS schema variant passes linting
    test_e2e_schema_violations.py    — every schema violation is detected and reported
    test_e2e_directory_scanning.py   — directory-level linting scenarios
    test_e2e_cli_options.py          — CLI flag behaviour (--debug, etc.)

To add a new e2e test, import the fixtures you need and write a function whose
name begins with ``test_``.  Every test function must carry a fully-compliant
ATS docstring (Objective, Approvals, Test steps) — we dogfood our own tool.

ATS docstring schema quick reference
-------------------------------------
Mandatory sections (must appear in every test-function docstring):

    Objective:
        <one-line description of what this test verifies>

    Approvals:
        - <acceptance criterion 1>
        - <acceptance criterion 2>

    Test steps:
        1. <action>
        2. Verify that <expected outcome>

Optional sections:

    Preconditions:
        1. <setup step>

    Data-driven-test:
        - <dataset entry>
"""

import textwrap
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ats_linter.cli import app

# ---------------------------------------------------------------------------
# CLI runner
# ---------------------------------------------------------------------------


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

        result = run_linter(str(some_dir), extra_args=["--debug"])
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

        test_file = write_test_file("test_example.py", source_code)
        assert test_file.exists()
    """

    def _write(filename: str, content: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path

    return _write


# ---------------------------------------------------------------------------
# Reusable ATS-compliant docstring templates
# ---------------------------------------------------------------------------


@pytest.fixture
def ats_minimal_docstring() -> str:
    """Return the smallest valid ATS docstring (all three mandatory sections).

    Use this when your test only needs *a* compliant docstring, not a specific one.

    Example::

        def test_something(write_test_file, run_linter, ats_minimal_docstring):
            f = write_test_file("test_x.py", make_test_module([("test_x", ats_minimal_docstring)]))
            assert run_linter(str(f)).exit_code == 0
    """
    return textwrap.dedent(
        """\
        Objective:
            Verify that the feature under test behaves correctly.

        Approvals:
            - The feature produces the expected output

        Test steps:
            1. Invoke the feature with valid input
            2. Verify that the output matches the expected value
        """
    )


@pytest.fixture
def ats_docstring_with_preconditions() -> str:
    """Return a fully-compliant ATS docstring that includes the optional Preconditions section."""
    return textwrap.dedent(
        """\
        Objective:
            Verify that the feature behaves correctly when preconditions are met.

        Approvals:
            - The feature produces the expected output under stated preconditions

        Preconditions:
            1. The system is in a known, clean initial state
            2. All required dependencies are available

        Test steps:
            1. Set up the system according to the preconditions
            2. Invoke the feature with valid input
            3. Verify that the output matches the expected value
        """
    )


@pytest.fixture
def ats_docstring_with_data_driven() -> str:
    """Return a fully-compliant ATS docstring that includes the optional Data-driven-test section."""
    return textwrap.dedent(
        """\
        Objective:
            Validate multiple input/output pairs to ensure the feature handles
            a range of data correctly.

        Approvals:
            - Each dataset entry produces the correct output

        Data-driven-test:
            - input=1  expected=2
            - input=5  expected=10
            - input=10 expected=20

        Test steps:
            1. For each dataset entry, invoke the feature with the given input
            2. Verify that the output equals the expected value
        """
    )


@pytest.fixture
def ats_docstring_with_matched_approvals() -> str:
    """Return an ATS docstring where the Approvals count exactly equals the verify-step count."""
    return textwrap.dedent(
        """\
        Objective:
            Verify that two independent calculations both produce the correct result
            and that their approval criteria match the verify steps.

        Approvals:
            - First calculation produces the expected result
            - Second calculation produces the expected result

        Test steps:
            1. Perform the first calculation
            2. Verify that the first result matches the expected value
            3. Perform the second calculation
            4. Verify that the second result matches the expected value
        """
    )


# ---------------------------------------------------------------------------
# ATS-non-compliant docstring constants (used by violation tests)
# ---------------------------------------------------------------------------

#: Docstring missing the mandatory Objective section.
DOCSTRING_MISSING_OBJECTIVE = textwrap.dedent(
    """\
    Approvals:
        - The result is correct

    Test steps:
        1. Do something
        2. Verify that the result is correct
    """
)

#: Docstring missing the mandatory Approvals section.
DOCSTRING_MISSING_APPROVALS = textwrap.dedent(
    """\
    Objective:
        Verify that the feature works as expected.

    Test steps:
        1. Invoke the feature
        2. Verify that the result is correct
    """
)

#: Docstring missing the mandatory Test steps section.
DOCSTRING_MISSING_TEST_STEPS = textwrap.dedent(
    """\
    Objective:
        Verify that the feature works as expected.

    Approvals:
        - The result is correct
    """
)

#: Docstring where Approvals count (2) does not match verify-step count (3).
DOCSTRING_MISMATCHED_APPROVALS_AND_VERIFY_STEPS = textwrap.dedent(
    """\
    Objective:
        Verify that approval count and verify-step count must match.

    Approvals:
        - First approval criterion
        - Second approval criterion

    Test steps:
        1. Perform the first action
        2. Verify that the first criterion is met
        3. Verify that the second criterion is met
        4. Verify that a third unexpected criterion is also met
    """
)


# ---------------------------------------------------------------------------
# Source-code generation helpers
# ---------------------------------------------------------------------------


def make_test_module(functions: list[tuple[str, str | None]]) -> str:
    """Render a Python source string containing the given test functions.

    Each element of *functions* is a ``(name, docstring)`` pair.  Pass
    ``None`` as the docstring to generate a function with no docstring at all.

    Args:
        functions: Sequence of ``(function_name, docstring_or_None)`` pairs.

    Returns:
        A Python source string suitable for writing to a ``.py`` file.

    Example::

        src = make_test_module([
            ("test_add", "Objective:\\n    ...\\n\\nApprovals:\\n    - ...\\n\\nTest steps:\\n    1. ..."),
            ("test_sub", None),  # no docstring — will fail linting
        ])
    """
    lines: list[str] = []
    for name, docstring in functions:
        lines.append(f"def {name}():")
        if docstring:
            lines.append(f'    """{docstring}"""')
        lines.append("    assert True")
        lines.append("")
    return "\n".join(lines)


def make_test_class_module(class_name: str, methods: list[tuple[str, str | None]]) -> str:
    """Render a Python source string containing a single test class.

    The class must be named with a ``Test`` prefix so the linter recognises it.

    Args:
        class_name: Name of the test class (must start with ``Test``).
        methods: Sequence of ``(method_name, docstring_or_None)`` pairs.

    Returns:
        A Python source string suitable for writing to a ``.py`` file.

    Example::

        src = make_test_class_module("TestCalculator", [
            ("test_add", compliant_docstring),
            ("test_sub", compliant_docstring),
        ])
    """
    lines: list[str] = [f"class {class_name}:"]
    for name, docstring in methods:
        lines.append(f"    def {name}(self):")
        if docstring:
            lines.append(f'        """{docstring}"""')
        lines.append("        assert True")
        lines.append("")
    return "\n".join(lines)
