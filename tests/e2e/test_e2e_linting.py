"""End-to-end tests for the ats-linter CLI.

These tests exercise the real application pipeline:
  file collection → AST parsing → docstring linting → exit code

Each test is self-contained and uses temporary files so that results are
deterministic regardless of the host environment.  The tests are written
using the ATS schema themselves, serving as a living example of compliant,
high-quality test documentation.

ATS mandatory sections reminder:
    Objective   – what the test verifies
    Approvals   – acceptance criteria (dash list)
    Test steps  – numbered execution steps (lines starting with
                  "Verify that …" are counted as verify steps)

Optional sections:
    Preconditions     – numbered setup requirements
    Data-driven-test  – dash list of data variants
"""

import textwrap

import pytest

# ---------------------------------------------------------------------------
# Reusable docstring building blocks
# ---------------------------------------------------------------------------

_FULL_COMPLIANT_DOCSTRING = textwrap.dedent(
    """\
    Objective:
        {objective}

    Approvals:
        - {approval}

    Test steps:
        1. {step}
        2. Verify that {verify}
    """
)

_COMPLIANT_WITH_PRECONDITIONS = textwrap.dedent(
    """\
    Objective:
        Verify that the feature behaves correctly under controlled conditions.

    Approvals:
        - The feature produces the expected output

    Preconditions:
        1. The system is in a known good state

    Test steps:
        1. Invoke the feature with valid input
        2. Verify that the output matches the expected value
    """
)

_COMPLIANT_WITH_DATA_DRIVEN = textwrap.dedent(
    """\
    Objective:
        Validate multiple input/output pairs for a calculation function.

    Approvals:
        - Each input produces the correct output

    Data-driven-test:
        - input=1 expected=2
        - input=2 expected=4

    Test steps:
        1. Run the calculation with each dataset entry
        2. Verify that the result equals the expected value
    """
)

_MISSING_OBJECTIVE = textwrap.dedent(
    """\
    Approvals:
        - Something passes

    Test steps:
        1. Do something
        2. Verify that it passes
    """
)

_MISSING_APPROVALS = textwrap.dedent(
    """\
    Objective:
        Ensure the feature works.

    Test steps:
        1. Do something
        2. Verify that it works
    """
)

_MISSING_TEST_STEPS = textwrap.dedent(
    """\
    Objective:
        Ensure the feature works.

    Approvals:
        - The feature works
    """
)

_MISMATCHED_APPROVALS_AND_VERIFY_STEPS = textwrap.dedent(
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
        4. Verify that a third (unexpected) criterion is also met
    """
)


# ---------------------------------------------------------------------------
# Helper: build a complete Python test-file string from (name, docstring) pairs
# ---------------------------------------------------------------------------


def _make_module(test_functions: list[tuple[str, str | None]]) -> str:
    """Render a Python source string with the given test functions.

    Args:
        test_functions: List of (function_name, docstring_or_None) tuples.

    Returns:
        A Python source string ready to be written to a .py file.

    """
    lines = []
    for name, docstring in test_functions:
        lines.append(f"def {name}():")
        if docstring:
            lines.append(f'    """{docstring}    """')
        lines.append("    assert True")
        lines.append("")
    return "\n".join(lines)


def _make_class_module(class_name: str, methods: list[tuple[str, str | None]]) -> str:
    """Render a Python source string with a single TestClass.

    Args:
        class_name: Name of the test class (must start with "Test").
        methods: List of (method_name, docstring_or_None) tuples.

    Returns:
        A Python source string ready to be written to a .py file.

    """
    lines = [f"class {class_name}:"]
    for name, docstring in methods:
        lines.append(f"    def {name}(self):")
        if docstring:
            lines.append(f'        """{docstring}        """')
        lines.append("        assert True")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# E2E tests — positive scenarios (linter should exit 0)
# ---------------------------------------------------------------------------


class TestCompliantTestFilesPassLinting:
    """Group of scenarios where all test functions satisfy the ATS schema.

    These tests show *exactly* what a passing test file looks like and confirm
    that ats-linter exits successfully (code 0) when the schema is followed.
    """

    def test_single_function_with_all_mandatory_sections_passes(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that a single test function containing all mandatory ATS
            sections (Objective, Approvals, Test steps) is accepted by the
            linter.

        Approvals:
            - The linter exits with code 0
            - The output contains the PASSED banner

        Test steps:
            1. Write a test file whose only function has a fully-compliant
               ATS docstring
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
            4. Verify that the output contains "PASSED"
        """
        docstring = _FULL_COMPLIANT_DOCSTRING.format(
            objective="Ensure that 1 + 1 equals 2.",
            approval="The arithmetic result is correct",
            step="Compute 1 + 1",
            verify="the result is 2",
        )
        test_file = write_test_file(
            "test_addition.py", _make_module([("test_addition", docstring)])
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0
        assert "PASSED" in result.output

    def test_multiple_functions_all_compliant_passes(self, run_linter, write_test_file):
        """Objective:
            Verify that a test file containing multiple fully-compliant
            functions is accepted without errors.

        Approvals:
            - The linter exits with code 0
            - Every function is reported as passing

        Test steps:
            1. Write a test file with three compliant test functions
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        doc = _FULL_COMPLIANT_DOCSTRING.format(
            objective="Ensure the feature behaves correctly.",
            approval="The feature returns the expected result",
            step="Invoke the feature with valid input",
            verify="the output matches the expected value",
        )
        test_file = write_test_file(
            "test_multi.py",
            _make_module(
                [
                    ("test_feature_a", doc),
                    ("test_feature_b", doc),
                    ("test_feature_c", doc),
                ]
            ),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0

    def test_optional_preconditions_section_passes(self, run_linter, write_test_file):
        """Objective:
            Verify that an optional Preconditions section alongside mandatory
            sections does not break linting.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a test file whose function includes the optional
               Preconditions section
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        test_file = write_test_file(
            "test_preconditions.py",
            _make_module([("test_with_preconditions", _COMPLIANT_WITH_PRECONDITIONS)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0

    def test_optional_data_driven_section_passes(self, run_linter, write_test_file):
        """Objective:
            Verify that an optional Data-driven-test section alongside
            mandatory sections does not break linting.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a test file whose function includes the optional
               Data-driven-test section
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        test_file = write_test_file(
            "test_data_driven.py",
            _make_module([("test_data_driven", _COMPLIANT_WITH_DATA_DRIVEN)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0

    def test_directory_with_only_compliant_files_passes(
        self, tmp_path, run_linter, write_test_file
    ):
        """Objective:
            Verify that linting an entire directory containing only compliant
            test files results in a successful exit.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Create a directory with two compliant test files
            2. Invoke ats-linter against the directory path
            3. Verify that the exit code is 0
        """
        doc = _FULL_COMPLIANT_DOCSTRING.format(
            objective="Ensure the module works end-to-end.",
            approval="The module produces the correct output",
            step="Call the module",
            verify="the output is correct",
        )
        (tmp_path / "test_module_a.py").write_text(
            _make_module([("test_module_a", doc)])
        )
        (tmp_path / "test_module_b.py").write_text(
            _make_module([("test_module_b", doc)])
        )

        result = run_linter(str(tmp_path))

        assert result.exit_code == 0

    def test_class_based_test_methods_pass(self, run_linter, write_test_file):
        """Objective:
            Verify that test methods inside a TestCase class with compliant
            ATS docstrings are accepted by the linter.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a test file containing a TestClass with two compliant
               test methods
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        doc = _FULL_COMPLIANT_DOCSTRING.format(
            objective="Validate a class-level test method.",
            approval="The method behaves as specified",
            step="Execute the method under test",
            verify="the result satisfies the acceptance criterion",
        )
        test_file = write_test_file(
            "test_class_based.py",
            _make_class_module(
                "TestMyFeature",
                [
                    ("test_method_one", doc),
                    ("test_method_two", doc),
                ],
            ),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0

    def test_matching_approvals_and_verify_steps_passes(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that when the number of Approvals exactly matches the
            number of "Verify that …" steps, the linter accepts the file.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a test file with two Approvals and two Verify-that steps
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        docstring = textwrap.dedent(
            """\
            Objective:
                Ensure that two independent calculations produce correct results.

            Approvals:
                - First calculation is correct
                - Second calculation is correct

            Test steps:
                1. Perform the first calculation
                2. Verify that the first result is correct
                3. Perform the second calculation
                4. Verify that the second result is correct
            """
        )
        test_file = write_test_file(
            "test_matched.py",
            _make_module([("test_matched_approvals", docstring)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# E2E tests — negative scenarios (linter should exit 1)
# ---------------------------------------------------------------------------


class TestNonCompliantTestFilesFailLinting:
    """Group of scenarios where the linter must detect schema violations.

    These tests demonstrate the *enforcement* value of ats-linter: each
    structural problem is caught and reported, and the process exits with
    a non-zero status code so CI pipelines fail fast.
    """

    def test_missing_objective_section_fails(self, run_linter, write_test_file):
        """Objective:
            Verify that a test function missing the mandatory Objective
            section is rejected by the linter.

        Approvals:
            - The linter exits with code 1
            - The output mentions the missing "Objective" section

        Test steps:
            1. Write a test file whose function has Approvals and Test steps
               but no Objective
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output references the missing Objective section
        """
        test_file = write_test_file(
            "test_no_objective.py",
            _make_module([("test_no_objective", _MISSING_OBJECTIVE)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Objective" in result.output

    def test_missing_approvals_section_fails(self, run_linter, write_test_file):
        """Objective:
            Verify that a test function missing the mandatory Approvals
            section is rejected by the linter.

        Approvals:
            - The linter exits with code 1
            - The output mentions the missing "Approvals" section

        Test steps:
            1. Write a test file whose function has Objective and Test steps
               but no Approvals
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output references the missing Approvals section
        """
        test_file = write_test_file(
            "test_no_approvals.py",
            _make_module([("test_no_approvals", _MISSING_APPROVALS)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Approvals" in result.output

    def test_missing_test_steps_section_fails(self, run_linter, write_test_file):
        """Objective:
            Verify that a test function missing the mandatory Test steps
            section is rejected by the linter.

        Approvals:
            - The linter exits with code 1
            - The output mentions the missing "Test steps" section

        Test steps:
            1. Write a test file whose function has Objective and Approvals
               but no Test steps
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output references the missing Test steps section
        """
        test_file = write_test_file(
            "test_no_steps.py",
            _make_module([("test_no_steps", _MISSING_TEST_STEPS)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Test steps" in result.output

    def test_function_without_docstring_fails(self, run_linter, write_test_file):
        """Objective:
            Verify that a test function with no docstring whatsoever is
            rejected by the linter with a clear error message.

        Approvals:
            - The linter exits with code 1
            - The output indicates a missing docstring

        Test steps:
            1. Write a test file whose function has no docstring
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output contains "docstring" or "FAILED"
        """
        test_file = write_test_file(
            "test_no_docstring.py",
            _make_module([("test_no_docstring", None)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "FAILED" in result.output

    def test_mismatched_approvals_and_verify_steps_fails(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that a mismatch between the number of Approval entries
            and the number of "Verify that …" steps causes the linter to fail.

        Approvals:
            - The linter exits with code 1
            - The output references a "Mismatch" between approvals and verify
              steps

        Test steps:
            1. Write a test file with two Approvals but three "Verify that"
               steps
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output contains "Mismatch"
        """
        test_file = write_test_file(
            "test_mismatch.py",
            _make_module(
                [("test_mismatch", _MISMATCHED_APPROVALS_AND_VERIFY_STEPS)]
            ),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Mismatch" in result.output

    def test_all_three_mandatory_sections_missing_fails(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that a test function whose docstring contains no ATS
            sections at all is rejected with errors for each mandatory section.

        Approvals:
            - The linter exits with code 1
            - Errors for Objective, Approvals, and Test steps all appear in
              the output

        Test steps:
            1. Write a test file whose function has a docstring that contains
               plain text but no ATS section headers
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output references all three missing sections
        """
        test_file = write_test_file(
            "test_plain_docstring.py",
            _make_module([("test_plain", "This test does something useful.")]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Objective" in result.output
        assert "Approvals" in result.output
        assert "Test steps" in result.output

    def test_directory_with_one_noncompliant_file_fails(
        self, tmp_path, run_linter, write_test_file
    ):
        """Objective:
            Verify that a directory containing a mix of compliant and
            non-compliant test files causes the linter to fail overall,
            ensuring that a single bad file cannot be silently ignored.

        Approvals:
            - The linter exits with code 1

        Test steps:
            1. Create a directory with one compliant and one non-compliant
               test file
            2. Invoke ats-linter against the directory path
            3. Verify that the exit code is 1
        """
        good_doc = _FULL_COMPLIANT_DOCSTRING.format(
            objective="Ensure this test is fully compliant.",
            approval="The result is correct",
            step="Execute the compliant function",
            verify="the result matches expectations",
        )
        (tmp_path / "test_good.py").write_text(
            _make_module([("test_good", good_doc)])
        )
        (tmp_path / "test_bad.py").write_text(
            _make_module([("test_bad", None)])  # no docstring
        )

        result = run_linter(str(tmp_path))

        assert result.exit_code == 1


# ---------------------------------------------------------------------------
# E2E tests — parametrised coverage of individual missing sections
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "missing_section, docstring",
    [
        pytest.param(
            "Objective",
            _MISSING_OBJECTIVE,
            id="missing-objective",
        ),
        pytest.param(
            "Approvals",
            _MISSING_APPROVALS,
            id="missing-approvals",
        ),
        pytest.param(
            "Test steps",
            _MISSING_TEST_STEPS,
            id="missing-test-steps",
        ),
    ],
)
def test_each_missing_mandatory_section_is_reported(
    run_linter, write_test_file, missing_section: str, docstring: str
):
    """Objective:
        Verify that each mandatory ATS section, when absent, is individually
        detected and named in the linter output.

    Approvals:
        - The linter exits with code 1 for every missing-section variant
        - The output names the specific section that is absent

    Test steps:
        1. Write a test file missing one specific mandatory section
        2. Invoke ats-linter against that file
        3. Verify that the exit code is 1
        4. Verify that the section name appears in the output
    """
    test_file = write_test_file(
        "test_missing_section.py",
        _make_module([("test_missing_section", docstring)]),
    )

    result = run_linter(str(test_file))

    assert result.exit_code == 1
    assert missing_section in result.output


# ---------------------------------------------------------------------------
# E2E tests — debug flag
# ---------------------------------------------------------------------------


def test_debug_flag_produces_additional_output(run_linter, write_test_file):
    """Objective:
        Verify that the --debug flag causes the linter to emit additional
        diagnostic messages, helping developers investigate failures.

    Approvals:
        - The linter exits with code 0 for a compliant file
        - The output contains DEBUG-level information when --debug is set

    Test steps:
        1. Write a fully-compliant test file
        2. Invoke ats-linter with --debug against that file
        3. Verify that the exit code is 0
        4. Verify that the output is longer than without --debug (i.e. more
           information was emitted)
    """
    doc = _FULL_COMPLIANT_DOCSTRING.format(
        objective="Verify debug output is present when --debug is passed.",
        approval="Debug output is emitted",
        step="Run the linter with --debug",
        verify="the output contains additional detail",
    )
    test_file = write_test_file(
        "test_debug.py", _make_module([("test_debug_flag", doc)])
    )

    result_normal = run_linter(str(test_file))
    result_debug = run_linter(str(test_file), extra_args=["--debug"])

    assert result_debug.exit_code == 0
    assert len(result_debug.output) > len(result_normal.output)
