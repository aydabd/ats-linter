"""E2E tests: schema violations are detected and reported by the linter.

These tests document and verify every *invalid* ATS docstring pattern — they
are the living specification of what the linter must catch and report.

Each test:
- Builds a tiny in-memory Python source file with a specific defect
- Runs the real ats-linter CLI against it
- Asserts exit code 1 and checks that the error message names the problem

Adding a new violation scenario?  Add a constant to conftest.py describing
the broken docstring, then write a focused test here.
"""

import pytest

from tests.e2e.conftest import (
    DOCSTRING_MISMATCHED_APPROVALS_AND_VERIFY_STEPS,
    DOCSTRING_MISSING_APPROVALS,
    DOCSTRING_MISSING_OBJECTIVE,
    DOCSTRING_MISSING_TEST_STEPS,
    make_test_module,
)


class TestMissingMandatorySectionsAreRejected:
    """Each missing mandatory section causes a targeted, named error."""

    def test_missing_objective_is_rejected_with_section_name_in_output(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that a test function missing the mandatory Objective section
            is rejected and that the error output explicitly names "Objective"
            so developers know exactly which section to add.

        Approvals:
            - The linter exits with code 1
            - The string "Objective" appears in the output

        Test steps:
            1. Write a test file whose function has Approvals and Test steps
               but no Objective section
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output contains the word "Objective"
        """
        test_file = write_test_file(
            "test_no_objective.py",
            make_test_module([("test_no_objective", DOCSTRING_MISSING_OBJECTIVE)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Objective" in result.output

    def test_missing_approvals_is_rejected_with_section_name_in_output(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that a test function missing the mandatory Approvals section
            is rejected and that the error output explicitly names "Approvals"
            so developers know exactly which section to add.

        Approvals:
            - The linter exits with code 1
            - The string "Approvals" appears in the output

        Test steps:
            1. Write a test file whose function has Objective and Test steps
               but no Approvals section
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output contains the word "Approvals"
        """
        test_file = write_test_file(
            "test_no_approvals.py",
            make_test_module([("test_no_approvals", DOCSTRING_MISSING_APPROVALS)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Approvals" in result.output

    def test_missing_test_steps_is_rejected_with_section_name_in_output(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that a test function missing the mandatory Test steps section
            is rejected and that the error output explicitly names "Test steps"
            so developers know exactly which section to add.

        Approvals:
            - The linter exits with code 1
            - The string "Test steps" appears in the output

        Test steps:
            1. Write a test file whose function has Objective and Approvals
               but no Test steps section
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output contains the phrase "Test steps"
        """
        test_file = write_test_file(
            "test_no_steps.py",
            make_test_module([("test_no_steps", DOCSTRING_MISSING_TEST_STEPS)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Test steps" in result.output

    def test_all_mandatory_sections_missing_reports_all_three(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that a test function whose docstring is plain prose (no ATS
            section headers at all) triggers errors for every mandatory section,
            giving developers a complete picture of what is missing.

        Approvals:
            - The linter exits with code 1
            - The output mentions "Objective", "Approvals", and "Test steps"

        Test steps:
            1. Write a test file whose function docstring is plain prose with no
               ATS section headers
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that all three mandatory section names appear in the output
        """
        plain_prose_docstring = "This test checks something important but has no ATS structure."
        test_file = write_test_file(
            "test_plain_prose.py",
            make_test_module([("test_plain_prose", plain_prose_docstring)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Objective" in result.output
        assert "Approvals" in result.output
        assert "Test steps" in result.output


class TestMissingDocstringIsRejected:
    """A test function with no docstring at all must be rejected."""

    def test_function_with_no_docstring_is_rejected(self, run_linter, write_test_file):
        """Objective:
            Verify that a test function that has no docstring whatsoever is
            rejected by the linter with a clear FAILED output, preventing
            completely undocumented tests from passing CI.

        Approvals:
            - The linter exits with code 1
            - The output contains the FAILED banner

        Test steps:
            1. Write a test file whose function body has no docstring
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output contains the word "FAILED"
        """
        test_file = write_test_file(
            "test_no_docstring.py",
            make_test_module([("test_no_docstring", None)]),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "FAILED" in result.output


class TestApprovalVerifyStepMismatchIsRejected:
    """Mismatched Approvals count vs Verify-that step count is a schema error."""

    def test_approval_count_mismatch_with_verify_steps_is_rejected(
        self, run_linter, write_test_file
    ):
        """Objective:
            Verify that when the number of Approvals entries does not match the
            number of "Verify that …" steps, the linter rejects the file and
            reports a clear mismatch error — enforcing traceability between
            acceptance criteria and verification actions.

        Approvals:
            - The linter exits with code 1
            - The output contains the word "Mismatch"

        Test steps:
            1. Write a test file whose docstring has two Approvals but three
               "Verify that" steps (2 ≠ 3)
            2. Invoke ats-linter against that file
            3. Verify that the exit code is 1
            4. Verify that the output contains the word "Mismatch"
        """
        test_file = write_test_file(
            "test_mismatch.py",
            make_test_module(
                [
                    (
                        "test_approval_count_mismatch",
                        DOCSTRING_MISMATCHED_APPROVALS_AND_VERIFY_STEPS,
                    )
                ]
            ),
        )

        result = run_linter(str(test_file))

        assert result.exit_code == 1
        assert "Mismatch" in result.output


# ---------------------------------------------------------------------------
# Parametrised: every mandatory section, when missing, is individually reported
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "missing_section, docstring",
    [
        pytest.param(
            "Objective",
            DOCSTRING_MISSING_OBJECTIVE,
            id="objective-section-missing",
        ),
        pytest.param(
            "Approvals",
            DOCSTRING_MISSING_APPROVALS,
            id="approvals-section-missing",
        ),
        pytest.param(
            "Test steps",
            DOCSTRING_MISSING_TEST_STEPS,
            id="test-steps-section-missing",
        ),
    ],
)
def test_each_mandatory_section_when_missing_is_individually_named_in_output(
    run_linter,
    write_test_file,
    missing_section: str,
    docstring: str,
):
    """Objective:
        Verify that when any single mandatory section is absent, the linter
        names that specific section in the error output — ensuring that error
        messages are actionable and point developers directly to the problem.

    Approvals:
        - The linter exits with code 1 for every missing-section variant
        - The error output names exactly the missing section

    Test steps:
        1. Write a test file whose function is missing one specific mandatory
           section
        2. Invoke ats-linter against that file
        3. Verify that the exit code is 1
        4. Verify that the missing section name appears in the output
    """
    test_file = write_test_file(
        "test_single_missing_section.py",
        make_test_module([("test_single_missing_section", docstring)]),
    )

    result = run_linter(str(test_file))

    assert result.exit_code == 1
    assert missing_section in result.output
