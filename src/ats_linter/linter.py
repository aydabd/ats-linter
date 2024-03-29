"""Copyright (c) 2023 Aydin Abdi

Module to lint test files.

This module provides a class to lint test files.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from threading import Lock
from typing import Any, Dict, List

from loguru import logger

from ats_linter.data_classes import Section, TestCase
from ats_linter.description import (
    TestDescription,
    SECTION_OBJECTIVE,
    SECTION_APPROVALS,
    SECTION_PRECONDITIONS,
    SECTION_DATA_DRIVEN_TEST,
    SECTION_TEST_STEPS,
)

# Comment out to enable logging
logger.disable("__name__")

MANDATORY_SECTIONS = [SECTION_OBJECTIVE, SECTION_APPROVALS, SECTION_TEST_STEPS]
OPTIONAL_SECTIONS = [SECTION_PRECONDITIONS, SECTION_DATA_DRIVEN_TEST]
SECTION_NAMES = MANDATORY_SECTIONS + OPTIONAL_SECTIONS

MISSING_SECTION_ERROR_MESSAGE = "Missing '{section_name}' section"
MISMATCH_APPROVALS_VERIFY_ERROR_MESSAGE = (
    "Mismatch between amount of 'Approvals'='{approvals}'"
    "and 'Verify steps'='{verifies}' sections"
)


@dataclass(frozen=True)
class ATSTestCase:
    """Represents a ATS test case.

    Parameters:
        test_case: The test case.
        test_description: ATS test case description :class: `TestDescription`.
    """

    test_case: TestCase
    test_description: TestDescription = field(
        init=False, default_factory=TestDescription
    )

    def __post_init__(self):
        """Post init method to parse docstring and create sections."""
        self.test_description = TestDescription(self.test_case.docstring)
        logger.debug(f"ATS test description:{self.test_description}")

    def __dict__(self) -> Dict[str, Any]:
        """Return the ATS test description as a dict.

        Returns:
            The ATS test description as a dict.
        """
        return asdict(self.test_description)

    def __len__(self) -> int:
        """Return number of verify steps.

        Returns:
            Number of verify steps.
        """
        nbr_of_verify_steps = self.test_description.verify_steps.__len__()
        logger.debug(
            f"Verify steps: {self.test_description.verify_steps}, "
            f"number of verify steps: {nbr_of_verify_steps}"
        )
        return nbr_of_verify_steps


@dataclass
class ATSTestCasesFactory:
    """Factory class to create :class: `ATSTestCase` objects.

    Parameters:
        test_cases: The list of :class: `TestCase` objects.
        ats_test_cases: The list of :class: `ATSTestCase` objects.
    """

    test_cases: List[TestCase]
    ats_test_cases: List[ATSTestCase] = field(init=False, default_factory=list)

    def __post_init__(self):
        """Post init method to create :class: `ATSTestCase` objects."""
        self._create_ats_test_cases()

    def _create_ats_test_cases(self) -> None:
        """Create :class: `ATSTestCase` objects from the test cases."""
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._create_ats_test_case, test_case)
                for test_case in self.test_cases
            }
            for future in as_completed(futures):
                self.ats_test_cases.append(future.result())

    def _create_ats_test_case(self, test_case: TestCase) -> ATSTestCase:
        """Create a :class: `ATSTestCase` object from a test case.

        Args:
            test_case: The test case to create a :class: `ATSTestCase` object from.

        Returns:
            The :class: `ATSTestCase` object created from the test case.
        """
        return ATSTestCase(test_case)

    def __len__(self) -> int:
        """Return number of :class: `ATSTestCase` objects.

        Returns:
            Number of :class: `ATSTestCase` objects.
        """
        return len(self.ats_test_cases)


@dataclass
class LintResult:
    module_name: str
    class_name: str
    test_name: str
    sections: List[Section]
    result: bool


@dataclass
class LintTestCase:
    """Class to lint ATS test cases.

    Parameters:
        ats_test_case: The ATS test case :class: `ATSTestCase`.
        test_case: The test case :class: `TestCase` to lint.
        test_description: The ATS test case description :class: `TestDescription`.
        sections: The list of sections in the test case.

        Example:
            >>> from ats_linter.test_data_classes import TestCase
            >>> from ats_linter.test_description import TestDescription
            >>> from ats_linter.linter import LintTestCase
            >>> test_case = TestCase(
            ...     name="Test case name",
            ...     docstring="Test case description",
            ...     test_steps=["Test step 1", "Test step 2"],
            ...     verify_steps=["Verify step 1", "Verify step 2"],
            ... )
            >>> test_case_linter = LintTestCase(test_case)
            >>> test_case_linter.lint()
            >>> test_case_linter.sections
    """

    ats_test_case: ATSTestCase
    test_case: TestCase = field(init=False, default_factory=TestCase)
    test_description: TestDescription = field(
        init=False, default_factory=TestDescription
    )
    sections: List[Section] = field(init=False, default_factory=list)
    lint_result: LintResult = field(init=False, default_factory=LintResult)

    def __post_init__(self):
        """Post init method to parse docstring and create sections."""
        self.test_case = self.ats_test_case.test_case
        self.test_description = self.ats_test_case.test_description
        self.sections = [
            Section(name=section_name, error_message=None)
            for section_name in SECTION_NAMES
        ]
        # self.lint_result = LintResult(

    def _check_section_presence(self, section: Section) -> None:
        """Check the presence of a section in the docstring.

        Args:
            section: The section to check.
        """
        dict_docstring = self.test_description
        try:
            section_content = getattr(
                dict_docstring, section.name.lower().replace(" ", "_")
            )
            if not section_content:
                section.error_message = MISSING_SECTION_ERROR_MESSAGE.format(
                    section_name=section.name
                )
        except AttributeError:
            section.error_message = MISSING_SECTION_ERROR_MESSAGE.format(
                section_name=section.name
            )

    def _check_sections(self, section_names: List[str]) -> None:
        """Check the presence of multiple sections in the docstring.

        Args:
            section_names: The list of section names to check.
        """
        for section_name in section_names:
            section = next(
                (section for section in self.sections if section.name == section_name),
                None,
            )
            if section.name in MANDATORY_SECTIONS:
                self._check_section_presence(section)

    def _check_mandatory_sections(self) -> None:
        """Check the presence of mandatory sections."""
        self._check_sections(MANDATORY_SECTIONS)

    def _check_matching_approvals_and_steps(self) -> None:
        """Check if the number of approvals matches the number of verify steps."""
        nbr_of_approvals = len(self.test_description.approvals)
        nbr_of_verify_steps = len(self)  # type: ignore
        logger.debug(f"Number of approvals: {nbr_of_approvals}")
        logger.debug(f"Number of verify steps: {nbr_of_verify_steps}")
        if (
            nbr_of_approvals
            and nbr_of_verify_steps
            and nbr_of_approvals != nbr_of_verify_steps
        ):
            self.sections.append(
                Section(
                    name="matching_approvals_steps",
                    error_message=MISMATCH_APPROVALS_VERIFY_ERROR_MESSAGE.format(
                        approvals=nbr_of_approvals,
                        verifies=nbr_of_verify_steps,
                    ),
                )
            )

    def lint(self) -> bool:
        """Lint the test case docstring and return the linting result.

        Returns:
            True if the test case docstring passes linting, False otherwise.
        """
        self._check_mandatory_sections()
        self._check_matching_approvals_and_steps()

        failed_sections = {
            section.name: section.error_message
            for section in self.sections
            if section.error_message
        }

        if failed_sections:
            logger.error(
                f"Test case '{self.test_case.name}' "
                f"failed linting for the following reasons:"
            )
            logger.error(
                "\n".join(
                    f"- {section}: {error}"
                    for section, error in failed_sections.items()
                )
            )
            return False

        logger.info(f"Test case '{self.test_case.name}' passed linting.")
        return True


class ATSTestCasesLinter:
    """Class to lint multiple ATS test cases.

    Parameters:
        ats_test_cases: The list of ATS test cases to lint.

        Example:
            >>> from ats_linter.test_data_classes import TestCase
            >>> from ats_linter.test_description import TestDescription
            >>> from ats_linter.linter import ATSTestCasesLinter
            >>> test_case_1 = TestCase(
            ...     name="Test case name 1",
            ...     docstring="Test case description 1",
            ...     test_steps=["Test step 1", "Test step 2"],
            ...     verify_steps=["Verify step 1", "Verify step 2"],
            ... )
            >>> test_case_2 = TestCase(
            ...     name="Test case name 2",
            ...     docstring="Test case description 2",
            ...     test_steps=["Test step 1", "Test step 2"],
            ...     verify_steps=["Verify step 1", "Verify step 2"],
            ... )
            >>> ats_test_cases_linter = ATSTestCasesLinter([test_case_1, test_case_2])
            >>> ats_test_cases_linter.lint()
    """

    ats_test_cases: List[ATSTestCase]
    lint_results: Dict[str, Any] = field(init=False, default_factory=dict)

    def __post_init__(self):
        """Post init method to lint ATS test cases in parallel."""
        self.lint_results = {}

    def lint(self) -> bool:
        """Lint the test case docstring and return the linting result.

        Returns:
            True if the test case docstring passes linting, False otherwise.
        """
        max_workers = len(self.ats_test_cases)
        lock = Lock()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    self.lint_ats_test_case, ats_test_case, self.lint_results, lock
                )
                for ats_test_case in self.ats_test_cases
            ]
            for future in as_completed(futures):
                if not future.result():
                    return False

        return True

    @staticmethod
    def lint_ats_test_case(
        ats_test_case: ATSTestCase, lint_results: Dict[str, Any], lock: Lock
    ) -> bool:
        """Lint a single test case.

        Args:
            test_case: The test case to lint.

        Returns:
            True if the test case passes linting, False otherwise.
        """
        try:
            lint_result = ATSTestCasesLinter(ats_test_case).lint()

            # Ensure that the dictionary is accessed in a thread-safe manner
            with lock:
                # Add the lint result to the dictionary
                lint_results.update(
                    {ats_test_case.test_case.name: {"status": lint_result}}
                )
        except Exception as e:
            logger.error(
                f"Failed to lint test case '{ats_test_case.test_case.name}': {e}"
            )

            with lock:
                lint_results[ats_test_case.test_case.name]["status"] = lint_result

        return lint_result
