"""Copyright (c) 2023 Aydin Abdi

This module encapsulates the logic of parsing test case test descriptions.
"""

from dataclasses import asdict, dataclass, field
from textwrap import dedent
from typing import Any, Dict, List, Optional

from loguru import logger

# Disable logger for this module
logger.disable(__name__)

SECTION_VERIFY = "Verify"
SECTION_OBJECTIVE = "Objective"
SECTION_APPROVALS = "Approvals"
SECTION_PRECONDITIONS = "Preconditions"
SECTION_DATA_DRIVEN_TEST = "Data-driven-test"
SECTION_TEST_STEPS = "Test steps"


@dataclass(frozen=True)
class TestDescription:
    """Represents a test case test description.

    Parameters:
        objective: The objective of the test.
        approvals: The approval criteria of the test.
        preconditions: The preconditions of the test. None if not provided.
        data_driven_test: The data-driven test descriptions. None if not provided.
        test_steps: The steps to execute the test.
        verify_steps: The steps that verifies test.
    """
    __test__ = False

    docstring: str
    objective: Optional[str] = field(default=None)
    approvals: List[str] = field(default_factory=list)
    preconditions: Optional[Dict[int, str]] = field(default_factory=dict)
    data_driven_test: Optional[List[str]] = field(default_factory=list)
    test_steps: Dict[int, str] = field(default_factory=dict)
    verify_steps: Dict[int, str] = field(default_factory=dict)

    def __post_init__(self):
        """Post init method (no-op, parsing handled by factory)."""
        pass

    def __dict__(self) -> Dict[str, Any]:  # type: ignore
        """Return the test description as a dict.

        Returns:
            The test description as a dict.
        """
        return asdict(self)


class TestDescriptionFactory:
    @staticmethod
    def from_docstring(docstring: str) -> TestDescription:
        """Create a TestDescription from a docstring (compatibility alias)."""
        return TestDescriptionFactory.dataclass_test_docstring_factory(docstring)
    """Factory class to create a TestDescription instance."""

    @staticmethod
    def parse_dash_list_section(section: str) -> List[str]:
        """Parse dash(start with '-') list sections from the docstring.

        Args:
            section: The section string to parse.

        Returns:
            A list of items parsed from the section.
        """
        return [
            item.partition("-")[2].strip()
            for item in section.split("\n")
            if item.partition("-")[2].strip()
        ]

    @staticmethod
    def parse_numbered_list_section(section: str) -> Dict[int, str]:
        """Parse numbered(1. 2. 3.) list sections from the docstring.

        Args:
            section: The section string to parse.

        Returns:
            A dictionary with list order as key and item as value.
        """
        return {
            i + 1: item.partition(".")[2].strip()
            for i, item in enumerate(section.split("\n"))
            if item.partition(".")[2].strip()
        }

    @staticmethod
    def parse_verify_steps(test_steps: Dict[int, str]) -> Dict[int, str]:
        """Parse verify steps from the test steps.

        Args:
            test_steps: The test steps to parse.

        Returns:
            A dictionary with key of test steps as key and verify step value as value.
        """
        return {
            key: value for key, value in test_steps.items() if SECTION_VERIFY in value
        }

    @staticmethod
    def dataclass_test_docstring_factory(docstring: str) -> TestDescription:
        """Factory method to create a TestDescription instance from a docstring.

        Args:
            docstring: The docstring to parse.

        Returns:
            :class: `TestDescription` instance.
        """
        import re
        section_headers = [
            SECTION_OBJECTIVE,
            SECTION_APPROVALS,
            SECTION_PRECONDITIONS,
            SECTION_DATA_DRIVEN_TEST,
            SECTION_TEST_STEPS,
            SECTION_VERIFY,
        ]
        header_regex = r"^([A-Za-z\- ]+):\s*$"
        lines = docstring.splitlines()
        sections = {}
        current_section = None
        current_content = []
        for line in lines:
            header_match = re.match(header_regex, line.strip())
            if header_match and header_match.group(1) in section_headers:
                if current_section:
                    sections[current_section] = "\n".join(current_content).rstrip()
                current_section = header_match.group(1)
                current_content = []
            elif current_section:
                current_content.append(line)
        if current_section:
            sections[current_section] = "\n".join(current_content).rstrip()
        logger.debug(f"Docstring sections: {sections}")

        objective = sections.get(SECTION_OBJECTIVE, None)
        if objective is not None:
            objective = objective.strip()
        approvals = TestDescriptionFactory.parse_dash_list_section(
            sections.get(SECTION_APPROVALS, "")
        )
        preconditions = (
            TestDescriptionFactory.parse_numbered_list_section(
                sections.get(SECTION_PRECONDITIONS, "")
            )
            if SECTION_PRECONDITIONS in sections and sections.get(SECTION_PRECONDITIONS, "") else None
        )
        data_driven_test = (
            TestDescriptionFactory.parse_dash_list_section(
                sections.get(SECTION_DATA_DRIVEN_TEST, "")
            )
            if SECTION_DATA_DRIVEN_TEST in sections and sections.get(SECTION_DATA_DRIVEN_TEST, "") else None
        )
        test_steps = TestDescriptionFactory.parse_numbered_list_section(
            sections.get(SECTION_TEST_STEPS, "")
        )

        # Extract verify steps: prefer dedicated Verify: section, else extract from Test steps lines containing 'Verify that'
        if SECTION_VERIFY in sections and sections.get(SECTION_VERIFY, "").strip():
            verify_steps = TestDescriptionFactory.parse_numbered_list_section(
                sections.get(SECTION_VERIFY, "")
            )
        else:
            # Extract from test_steps values containing 'Verify that'
            verify_steps = {k: v for k, v in test_steps.items() if v.strip().startswith("Verify that")}

        logger.debug(f"Test steps: {test_steps}")
        logger.debug(f"Verify steps: {verify_steps}")

        return TestDescription(
            docstring=docstring,
            objective=objective,
            approvals=approvals,
            preconditions=preconditions,
            data_driven_test=data_driven_test,
            test_steps=test_steps,
            verify_steps=verify_steps,
        )
