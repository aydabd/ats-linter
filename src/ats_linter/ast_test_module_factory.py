"""Copyright (c) 2023 Aydin Abdi

ASTTestModuleFactory is a factory class for creating test modules
based on Python's AST (Abstract Syntax Tree).
It encapsulates the logic of parsing an AST from a Python test file,
extracting test module, classes, cases, and pytest fixtures.
Test cases are based on unittest.TestCase and pytest test functions and
fixtures based on pytest fixtures.
"""

import ast
from dataclasses import dataclass
from typing import Callable, List, Sequence

from ats_linter.data_classes import Entity, PytestFixture, TestCase, TestClass

TEST_PREFIX = "test_"
TEST_CLASS_PREFIX = "Test"
PY_EXTENSION = ".py"
PYTEST_ID = "pytest"
PYTEST_FIXTURE = "fixture"


@dataclass
class ASTTestModuleFactory:
    """Test module factory based on Python's AST (Abstract Syntax Tree).

    This class encapsulates the logic of parsing an AST from a Python test file,
    extracting test module, classes, cases, and pytest fixtures.
    Test cases are based on unittest.TestCase and
    pytest test functions and fixtures based on pytest fixtures.
    """

    @staticmethod
    def get_test_classes(nodes: List[ast.AST]) -> List[ast.ClassDef]:
        """Get test classes from a list of AST nodes.

        Args:
            nodes: The list of AST nodes.

        Returns:
            The test classes from the list of nodes.
        """
        return [
            node
            for node in nodes
            if isinstance(node, ast.ClassDef)
            and node.name.startswith(TEST_CLASS_PREFIX)
        ]

    @staticmethod
    def get_function_nodes(nodes: List[ast.AST]) -> List[ast.FunctionDef]:
        """Get function nodes from a list of AST nodes.

        Args:
            nodes: The list of AST nodes.

        Returns:
            The function nodes from the list of nodes.
        """
        return [node for node in nodes if isinstance(node, ast.FunctionDef)]

    @staticmethod
    def is_test_case(node: ast.AST) -> bool:
        """Check if a node is a test case.

        Args:
            node: The node to check.

        Returns:
            Boolean value indicating whether the node is a test case.
        """
        ast.AST.node = node  # type: ignore
        return node.name.lower().startswith(TEST_PREFIX)  # type: ignore

    @staticmethod
    def is_pytest_fixture(node: ast.AST) -> bool:
        """Check if a node is a pytest fixture.

        Args:
            node: The node to check.

        Returns:
            Boolean value indicating whether the node is a pytest fixture.
        """
        return any(
            isinstance(deco, ast.Call)
            and isinstance(deco.func, ast.Attribute)
            and isinstance(deco.func.value, ast.Name)
            and deco.func.value.id == PYTEST_ID
            and deco.func.attr == PYTEST_FIXTURE
            for deco in node.decorator_list  # type: ignore
        )

    # type: ignore
    @staticmethod
    def parse_test_classes(
        test_classes: List[ast.ClassDef],
    ) -> List[TestClass]:
        """Parse test classes.

        Args:
            test_classes: The test classes to parse.

        Returns:
            The parsed test classes.
        """
        parsed_test_classes = []
        for test_class in test_classes:
            class_nodes = list(ast.iter_child_nodes(test_class))
            parsed_test_class = TestClass(
                test_class.name,
                ast.get_docstring(test_class),
                ASTTestModuleFactory.extract_entities(
                    class_nodes, TestCase, ASTTestModuleFactory.is_test_case
                ),
                ASTTestModuleFactory.extract_entities(
                    class_nodes, PytestFixture, ASTTestModuleFactory.is_pytest_fixture
                ),
            )
            parsed_test_classes.append(parsed_test_class)
        return parsed_test_classes

    @staticmethod
    def extract_entities(
        nodes: List[ast.AST], entity_class: Entity, condition: Callable[[ast.AST], bool]
    ) -> Sequence[Entity]:
        """Extract entities of a given type from the list of nodes.

        Args:
            nodes: A list of AST nodes to extract entities from.
            entity_class: The class of the entity to extract.
            condition: A function that defines the condition for entity extraction.

        Returns:
            A list of entity instances extracted from the nodes.
        """
        entities = []
        for node in nodes:
            if isinstance(node, ast.FunctionDef) and condition(node):
                docstring = ast.get_docstring(node)
                # Remove the last line of the function body if it is an expression
                code = "".join(
                    [
                        ast.unparse(line)
                        for line in node.body
                        if not isinstance(line, ast.Expr)
                    ]
                )
                entities.append(entity_class(node.name, docstring, code))
        return entities
