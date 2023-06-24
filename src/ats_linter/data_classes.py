"""Copyright (c) 2023 Aydin Abdi

This module defines the data classes used in this module.
"""
from typing import Dict, List, Optional, Union
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TestCase:
    """Represent a test case.

    Parameters:
        name: The name of the test case.
        docstring: The docstring of the test case.
        code: The code of the test case.
    """

    name: str
    docstring: str
    code: str


@dataclass(frozen=True)
class PytestFixture:
    """Represent a pytest fixture.

    Parameters:
        name: The name of the fixture.
        docstring: The docstring of the fixture.
        code: The code of the fixture.
    """

    name: str
    docstring: Optional[str]
    code: str


@dataclass(frozen=True)
class Entity:
    """Represent a generic entity in a test module.

    Parameters:
        name: The name of the entity.
        docstring: The docstring of the entity.
        code: The code of the entity.
    """

    name: str
    docstring: Optional[str]
    code: str


@dataclass(frozen=True)
class TestClass:
    """Represent a test class.

    Parameters:
        name: The name of the test class.
        docstring: The docstring of the test class.
        test_cases: The list of test cases in the class.
        fixtures: The list of fixtures in the class.
    """

    name: str
    docstring: Optional[str]
    test_cases: List[TestCase]
    fixtures: List[PytestFixture]

    def __len__(self) -> int:
        """Return the number of test cases.

        Returns:
            The number of test cases.
        """
        return len(self.test_cases)

    def __dict__(self) -> Dict[str, Union[int, List[Dict[str, str]]]]:  # type: ignore
        """Return the test class as a dict.

        Returns:
            The test class as a dict.
        """
        return {
            "test_cases": [asdict(test_case) for test_case in self.test_cases],
            "nbr_of_test_cases": len(self.test_cases),
            "fixtures": [asdict(fixture) for fixture in self.fixtures],
            "nbr_of_fixtures": len(self.fixtures),
        }


@dataclass(frozen=True)
class TestModule:
    """Represent a test module.

    Parameters:
        name: The name of the module.
        test_classes: The list of test classes in the module.
        test_cases: The list of test cases in the module.
        fixtures: The list of fixtures in the module.
    """

    name: str
    test_classes: List[TestClass]
    test_cases: List[TestCase]
    fixtures: List[PytestFixture]

    def __len__(self) -> int:
        """Return the number of test cases.

        Returns:
            The number of test cases
        """
        amount_of_test_cases = 0
        for test_class in self.test_classes:
            amount_of_test_cases += len(test_class)
        amount_of_test_cases += len(self.test_cases)
        return amount_of_test_cases

    def __dict__(self) -> Dict[str, Union[str, List[Dict[str, str]]]]:  # type: ignore
        """Return the test module as a dict.

        Returns:
            The test module as a dict.
        """
        return {
            "test_module": self.name,
            "test_classes": [asdict(test_class) for test_class in self.test_classes],
            "test_cases": [asdict(test_case) for test_case in self.test_cases],
            "fixtures": [asdict(fixture) for fixture in self.fixtures],
        }


@dataclass
class Section:
    """Represent a section in a test description for MHSTestLinter.

    Parameters:
        name: The name of the section.
        error_message: The error message of the section.
    """

    name: str
    error_message: Optional[str]

    def __dict__(self) -> Dict[str, Optional[str]]:  # type: ignore
        """Return the section as a dict.

        Returns:
            The section as a dict.
        """
        return {
            "name": self.name,
            "error_message": self.error_message,
        }
