"""E2E tests: directory-level linting scenarios.

These tests exercise ats-linter's file-discovery capability — the ability to
recurse into directories, find test files automatically, and aggregate results
across multiple files.

Real-world teams point the linter at their entire ``tests/`` directory, not at
individual files.  These tests verify that behaviour and demonstrate common
multi-file scenarios.
"""

from pathlib import Path

from tests.e2e.conftest import (
    DOCSTRING_MISSING_OBJECTIVE,
    make_test_module,
)


class TestDirectoryWithAllCompliantFiles:
    """A directory containing only compliant test files passes the linter."""

    def test_directory_with_multiple_compliant_files_is_accepted(
        self,
        tmp_path: Path,
        run_linter,
        ats_minimal_docstring,
    ):
        """Objective:
            Verify that pointing ats-linter at a directory containing several
            fully-compliant test files results in a successful exit — this is
            the standard CI use-case where the linter runs against the whole
            ``tests/`` directory.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Create a directory with three separate compliant test files
            2. Invoke ats-linter against the directory path
            3. Verify that the exit code is 0
        """
        for module_name in ("test_module_alpha", "test_module_beta", "test_module_gamma"):
            (tmp_path / f"{module_name}.py").write_text(
                make_test_module([(module_name, ats_minimal_docstring)])
            )

        result = run_linter(str(tmp_path))

        assert result.exit_code == 0

    def test_directory_passes_only_when_every_function_is_compliant(
        self,
        tmp_path: Path,
        run_linter,
        ats_minimal_docstring,
    ):
        """Objective:
            Verify that a directory with one file containing multiple functions
            — all of which are fully compliant — is accepted in full.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Create a directory with a single file that has three compliant
               functions
            2. Invoke ats-linter against the directory path
            3. Verify that the exit code is 0
        """
        (tmp_path / "test_multi_function.py").write_text(
            make_test_module(
                [
                    ("test_first_scenario", ats_minimal_docstring),
                    ("test_second_scenario", ats_minimal_docstring),
                    ("test_third_scenario", ats_minimal_docstring),
                ]
            )
        )

        result = run_linter(str(tmp_path))

        assert result.exit_code == 0


class TestDirectoryWithNonCompliantFiles:
    """A single non-compliant file causes the entire directory scan to fail."""

    def test_one_noncompliant_file_fails_the_whole_directory(
        self,
        tmp_path: Path,
        run_linter,
        ats_minimal_docstring,
    ):
        """Objective:
            Verify that when a directory contains a mix of compliant and
            non-compliant test files, the linter fails overall — a single bad
            file cannot be silently ignored in CI.

        Approvals:
            - The linter exits with code 1

        Test steps:
            1. Create a directory with one fully-compliant file and one file
               that has a function with no docstring
            2. Invoke ats-linter against the directory path
            3. Verify that the exit code is 1
        """
        (tmp_path / "test_good.py").write_text(
            make_test_module([("test_good_function", ats_minimal_docstring)])
        )
        (tmp_path / "test_bad.py").write_text(
            make_test_module([("test_bad_no_docstring", None)])
        )

        result = run_linter(str(tmp_path))

        assert result.exit_code == 1

    def test_one_file_with_missing_section_fails_the_whole_directory(
        self,
        tmp_path: Path,
        run_linter,
        ats_minimal_docstring,
    ):
        """Objective:
            Verify that even a single function missing one mandatory section
            causes the directory-level lint to fail, demonstrating that the
            linter enforces the schema across all discovered files.

        Approvals:
            - The linter exits with code 1

        Test steps:
            1. Create a directory with one fully-compliant file and one file
               whose function is missing the Objective section
            2. Invoke ats-linter against the directory path
            3. Verify that the exit code is 1
        """
        (tmp_path / "test_compliant.py").write_text(
            make_test_module([("test_compliant", ats_minimal_docstring)])
        )
        (tmp_path / "test_missing_objective.py").write_text(
            make_test_module([("test_missing_objective", DOCSTRING_MISSING_OBJECTIVE)])
        )

        result = run_linter(str(tmp_path))

        assert result.exit_code == 1

    def test_directory_with_only_noncompliant_files_fails(
        self,
        tmp_path: Path,
        run_linter,
    ):
        """Objective:
            Verify that a directory where every test file is non-compliant
            causes the linter to fail — there is no partial-pass scenario.

        Approvals:
            - The linter exits with code 1

        Test steps:
            1. Create a directory with two files, each containing a function
               with no docstring
            2. Invoke ats-linter against the directory path
            3. Verify that the exit code is 1
        """
        (tmp_path / "test_no_docstring_a.py").write_text(
            make_test_module([("test_no_docstring_a", None)])
        )
        (tmp_path / "test_no_docstring_b.py").write_text(
            make_test_module([("test_no_docstring_b", None)])
        )

        result = run_linter(str(tmp_path))

        assert result.exit_code == 1
