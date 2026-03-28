"""E2E tests: compliant ATS schemas are accepted by the linter.

These tests document and verify every *valid* ATS docstring shape — they are
the living specification of what correct test documentation looks like.
Reading these tests tells you exactly how to write a compliant test function.

Each test:
- Builds a tiny in-memory Python source file
- Runs the real ats-linter CLI against it
- Asserts exit code 0 and a PASSED banner

Adding a new shape?  Copy the closest test, adjust the docstring template,
and the parametrised test at the bottom will pick it up automatically.
"""

import textwrap

import pytest

from tests.e2e.conftest import (
    DOCSTRING_MISSING_APPROVALS,
    DOCSTRING_MISSING_OBJECTIVE,
    DOCSTRING_MISSING_TEST_STEPS,
    make_test_class_module,
    make_test_module,
)


class TestMandatorySectionsAreAccepted:
    """All three mandatory sections (Objective, Approvals, Test steps) satisfy the linter."""

    def test_function_with_all_mandatory_sections_is_accepted(
        self, run_linter, write_test_file, ats_minimal_docstring
    ):
        """Objective:
            Verify that a test function containing all three mandatory ATS
            sections (Objective, Approvals, Test steps) is accepted by the
            linter, proving that a minimal-yet-complete docstring is sufficient.

        Approvals:
            - The linter exits with code 0
            - The output contains the PASSED success banner

        Test steps:
            1. Write a test file whose only function has all three mandatory
               ATS sections in its docstring
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
            4. Verify that the output contains the word "PASSED"
        """
        test_file = write_test_file(
            "test_minimal.py",
            make_test_module([("test_minimal_ats_schema", ats_minimal_docstring)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0
        assert "PASSED" in result.output

    def test_multiple_functions_all_compliant_are_accepted(
        self, run_linter, write_test_file, ats_minimal_docstring
    ):
        """Objective:
            Verify that a test file containing several fully-compliant functions
            is accepted in full — not just the first function.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a test file with three compliant test functions
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        functions = [
            (f"test_feature_{letter}", ats_minimal_docstring)
            for letter in ("alpha", "beta", "gamma")
        ]
        test_file = write_test_file(
            "test_multi_function.py", make_test_module(functions)
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0

    def test_verify_that_steps_inside_test_steps_are_accepted(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that numbered steps beginning with "Verify that …" inside
            the Test steps section are parsed correctly and counted as verify
            steps without triggering any error.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a compliant docstring that uses inline "Verify that" steps
            2. Invoke ats-linter against the resulting file
            3. Verify that the exit code is 0
        """
        docstring = textwrap.dedent(
            """\
            Objective:
                Verify that inline verify-steps inside Test steps work correctly.

            Approvals:
                - The first verification passes
                - The second verification passes

            Test steps:
                1. Perform the first action
                2. Verify that the first outcome is correct
                3. Perform the second action
                4. Verify that the second outcome is correct
            """
        )
        test_file = write_test_file(
            "test_verify_steps.py",
            make_test_module([("test_inline_verify_steps", docstring)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0


class TestOptionalSectionsAreAccepted:
    """Optional sections (Preconditions, Data-driven-test) do not break linting."""

    def test_preconditions_section_is_accepted(
        self,
        run_linter,
        write_test_file,
        ats_docstring_with_preconditions,
    ):
        """Objective:
            Verify that the optional Preconditions section, when present
            alongside all mandatory sections, is accepted without errors.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a test file whose function includes the Preconditions section
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        test_file = write_test_file(
            "test_with_preconditions.py",
            make_test_module(
                [("test_with_preconditions", ats_docstring_with_preconditions)]
            ),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0

    def test_data_driven_section_is_accepted(
        self,
        run_linter,
        write_test_file,
        ats_docstring_with_data_driven,
    ):
        """Objective:
            Verify that the optional Data-driven-test section, when present
            alongside all mandatory sections, is accepted without errors.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a test file whose function includes the Data-driven-test
               section
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        test_file = write_test_file(
            "test_with_data_driven.py",
            make_test_module(
                [("test_with_data_driven", ats_docstring_with_data_driven)]
            ),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0

    def test_all_optional_sections_together_are_accepted(
        self,
        run_linter,
        write_test_file,
        ats_docstring_with_preconditions,
        ats_docstring_with_data_driven,
    ):
        """Objective:
            Verify that a test file where different functions each use a
            different optional section is accepted in full.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a test file with two functions — one using Preconditions
               and one using Data-driven-test
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        test_file = write_test_file(
            "test_all_optional.py",
            make_test_module(
                [
                    ("test_has_preconditions", ats_docstring_with_preconditions),
                    ("test_has_data_driven", ats_docstring_with_data_driven),
                ]
            ),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0


class TestClassBasedTestsAreAccepted:
    """Test methods inside a class with the Test prefix are linted correctly."""

    def test_class_methods_with_compliant_docstrings_are_accepted(
        self,
        run_linter,
        write_test_file,
        ats_minimal_docstring,
    ):
        """Objective:
            Verify that test methods inside a class whose name starts with
            "Test" are discovered and accepted when their docstrings are
            fully ATS-compliant.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a file containing a TestXxx class with two compliant
               test methods
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        methods = [
            ("test_first_method", ats_minimal_docstring),
            ("test_second_method", ats_minimal_docstring),
        ]
        test_file = write_test_file(
            "test_class_based.py",
            make_test_class_module("TestMyFeature", methods),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0


class TestApprovalCountMatchesVerifySteps:
    """Approval count and Verify-that step count parity is enforced and accepted."""

    def test_matching_approvals_and_verify_step_count_is_accepted(
        self,
        run_linter,
        write_test_file,
        ats_docstring_with_matched_approvals,
    ):
        """Objective:
            Verify that when the number of Approvals entries exactly equals the
            number of "Verify that …" steps, the linter accepts the file without
            reporting a mismatch error.

        Approvals:
            - The linter exits with code 0

        Test steps:
            1. Write a test file whose docstring has two Approvals and exactly
               two "Verify that" steps
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 0
        """
        test_file = write_test_file(
            "test_matched_counts.py",
            make_test_module(
                [("test_matched_counts", ats_docstring_with_matched_approvals)]
            ),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Parametrised: every valid schema variant (quick-check table)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture_name, test_id",
    [
        pytest.param("ats_minimal_docstring", "minimal-mandatory-sections"),
        pytest.param("ats_docstring_with_preconditions", "with-preconditions"),
        pytest.param("ats_docstring_with_data_driven", "with-data-driven"),
        pytest.param("ats_docstring_with_matched_approvals", "matched-approval-count"),
    ],
)
def test_every_compliant_schema_variant_passes_linting(
    request,
    run_linter,
    write_test_file,
    fixture_name: str,
    test_id: str,
):
    """Objective:
        Verify that every documented ATS docstring variant (minimal, with
        Preconditions, with Data-driven-test, with matched Approvals) is
        accepted by the linter, providing a single regression check across
        all supported schema shapes.

    Approvals:
        - The linter exits with code 0 for every schema variant

    Test steps:
        1. Obtain the docstring for the current schema variant via its
           fixture name
        2. Write a test file using that docstring
        3. Invoke ats-linter against that file
        4. Verify that the exit code is 0
    """
    docstring = request.getfixturevalue(fixture_name)
    test_file = write_test_file(
        f"test_{test_id.replace('-', '_')}.py",
        make_test_module([(f"test_{test_id.replace('-', '_')}", docstring)]),
    )

    result = run_linter(str(test_file))

    assert result.exit_code == 0
