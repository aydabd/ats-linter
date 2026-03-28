"""E2E tests: CLI flag and option behaviour.

These tests exercise ats-linter's command-line interface at the flag level,
independently of schema correctness.  They verify that each CLI option
produces the expected side-effect on output, exit code, and verbosity.

Adding a new flag?  Add it to the CLI, then add a focused test class here.
"""

from tests.e2e.conftest import make_test_module


class TestDebugFlag:
    """The --debug flag increases diagnostic verbosity without changing correctness."""

    def test_debug_flag_produces_more_output_than_default_run(
        self, run_linter, write_test_file, ats_minimal_docstring
    ):
        """Objective:
            Verify that passing --debug to ats-linter causes the CLI to emit
            additional diagnostic output compared to a run without the flag,
            helping developers trace how the linter processes their files.

        Approvals:
            - The linter exits with code 0 for a compliant file
            - The output length with --debug exceeds the output length without

        Test steps:
            1. Write a fully-compliant test file
            2. Invoke ats-linter once without --debug and record the output
            3. Invoke ats-linter again with --debug and record the output
            4. Verify that the exit code is 0 in the debug run
            5. Verify that the debug output is longer than the normal output
        """
        test_file = write_test_file(
            "test_debug.py",
            make_test_module([("test_with_debug_flag", ats_minimal_docstring)]),
        )

        result_normal = run_linter(str(test_file))
        result_debug = run_linter(str(test_file), extra_args=["--debug"])

        assert result_debug.exit_code == 0
        assert len(result_debug.output) > len(result_normal.output)

    def test_debug_flag_does_not_change_exit_code_on_compliant_file(
        self, run_linter, write_test_file, ats_minimal_docstring
    ):
        """Objective:
            Verify that the --debug flag does not change the exit code when
            the linted file is compliant — debug mode is purely additive and
            must not introduce false positives.

        Approvals:
            - Both the normal run and the --debug run exit with code 0

        Test steps:
            1. Write a fully-compliant test file
            2. Invoke ats-linter without --debug
            3. Invoke ats-linter with --debug
            4. Verify that both exit codes are 0
        """
        test_file = write_test_file(
            "test_debug_exit_code.py",
            make_test_module([("test_debug_exit_code", ats_minimal_docstring)]),
        )

        result_normal = run_linter(str(test_file))
        result_debug = run_linter(str(test_file), extra_args=["--debug"])

        assert result_normal.exit_code == 0
        assert result_debug.exit_code == 0

    def test_debug_flag_does_not_change_exit_code_on_noncompliant_file(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that the --debug flag does not change the exit code when
            the linted file is non-compliant — a failing file must still fail
            even in debug mode, so CI pipelines are not tricked.

        Approvals:
            - Both the normal run and the --debug run exit with code 1

        Test steps:
            1. Write a test file whose function has no docstring
            2. Invoke ats-linter without --debug
            3. Invoke ats-linter with --debug
            4. Verify that both exit codes are 1
        """
        test_file = write_test_file(
            "test_debug_noncompliant.py",
            make_test_module([("test_no_docstring", None)]),
        )

        result_normal = run_linter(str(test_file))
        result_debug = run_linter(str(test_file), extra_args=["--debug"])

        assert result_normal.exit_code == 1
        assert result_debug.exit_code == 1


class TestExplicitFilePath:
    """The linter can target a single file path instead of a directory."""

    def test_single_file_path_is_accepted_when_compliant(
        self, run_linter, write_test_file, ats_minimal_docstring
    ):
        """Objective:
            Verify that ats-linter correctly handles a single file path
            argument, accepting a compliant file without errors — a common
            use-case for pre-commit hooks that pass the staged file directly.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a fully-compliant test file
            2. Invoke ats-linter with the file's absolute path as the argument
            3. Verify that the exit code is 0
        """
        test_file = write_test_file(
            "test_single_file.py",
            make_test_module([("test_single_file_path", ats_minimal_docstring)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0

    def test_single_file_path_is_rejected_when_noncompliant(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that ats-linter correctly handles a single file path
            argument, rejecting a non-compliant file — ensuring that targeted
            file-by-file invocations (e.g. from a pre-commit hook) still
            enforce the schema.

        Approvals:
            - The linter exits with code 1

        Test steps:
            1. Write a test file whose function has no docstring
            2. Invoke ats-linter with the file's absolute path as the argument
            3. Verify that the exit code is 1
        """
        test_file = write_test_file(
            "test_single_bad_file.py",
            make_test_module([("test_no_docstring", None)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
