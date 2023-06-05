"""Copyright (c) 2023 Aydin Abdi

ASTProducer reads files and produces AST(Abstract Syntax Tree)s.
"""
import ast
import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from loguru import logger

from ats_linter.test_data_classes import TestModule, TestCase, PytestFixture
from ats_linter.ast_test_module_factory import (
    PY_EXTENSION,
    TEST_PREFIX,
    ASTTestModuleFactory,
)

# Comment out to enable logging
logger.disable("__name__")

SENTINEL = object()  # Define a sentinel value for the queue


@dataclass
class ASTProducer:
    """Read files and produce AST(Abstract Syntax Tree)s.

    This class encapsulates the logic of reading Python files and producing ASTs.
    The ASTs are produced asynchronously and put in a queue.

    Parameters:
        file_paths: The list of :class: `Path` objects of the Python files to parse.
        ast_tree_queue: The queue of ASTs produced from the Python files.
        task: The asyncio task that produces the ASTs.
    """

    file_paths: List[Path]
    ast_tree_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    task: Optional[asyncio.Task] = field(init=False, default=None)

    async def __aenter__(self) -> "ASTProducer":
        """Enter the context manager.

        Returns:
            The ASTProducer object.
        """
        self.task = asyncio.create_task(self.produce_ast_trees())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager.

        Args:
            exc_type: The type of the exception raised.
            exc_val: The value of the exception raised.
            exc_tb: The traceback of the exception raised.
        """
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        if exc_type:
            logger.error(f"Error parsing file: {exc_type}")

        await self.ast_tree_queue.put(
            SENTINEL
        )  # Put the sentinel in the queue to signal completion
        logger.debug("ASTProducer has finished producing ast_trees")

    async def produce_ast_trees(self) -> None:
        """Produce ASTs from the Python files.

        This method reads the Python files and produces ASTs from them.
        """
        for file_path in self.file_paths:
            ast_tree = self._get_ast_tree(file_path)
            if ast_tree:
                await self.ast_tree_queue.put((file_path, ast_tree))

    @staticmethod
    def _get_ast_tree(file_path: Path) -> ast.Module:
        """Get the abstract syntax tree (AST) of a Python file.

        Args:
            file_path: The path of the Python file.

        Returns:
            The AST of the Python file.
        """
        with file_path.open("r") as source:
            return ast.parse(source.read())

    @staticmethod
    def is_test_file(file_path: Path) -> bool:
        """Check if file is a test module.

        Args:
            file_path: The path of the file to check.

        Returns:
            Boolean value indicating whether the file is a test module.
        """
        return file_path.name.startswith(TEST_PREFIX) and file_path.name.endswith(
            PY_EXTENSION
        )


@dataclass
class ASTConsumer:
    """Parse ASTs into TestModule objects.

    This class encapsulates the logic of parsing ASTs into TestModule objects.
    The ASTs are consumed asynchronously from a queue.

    Parameters:
        ast_tree_queue: The queue of ASTs produced from the Python files.
        test_modules: The queue of TestModule objects produced from the ASTs.
        task: The asyncio task that consumes the ASTs.
    """

    ast_tree_queue: asyncio.Queue
    test_modules: List[TestModule]
    task: Optional[asyncio.Task] = field(init=False, default=None)

    async def __aenter__(self) -> "ASTConsumer":
        """Enter the context manager.

        Returns:
            The ASTConsumer object.
        """
        self.task = asyncio.create_task(self.consume_ast_trees())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager.

        Args:
            exc_type: The type of the exception raised.
            exc_val: The value of the exception raised.
            exc_tb: The traceback of the exception raised.
        """
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        if exc_type:
            logger.error(f"Exception {exc_type} has occurred")

        logger.debug("ASTConsumer has finished consuming ast_trees")

    async def consume_ast_trees(self) -> None:
        """Consume ASTs from the queue and parse them into TestModule objects.

        This method consumes ASTs from the queue and parses them into
        TestModule objects.
        The method will stop consuming ASTs when it encounters the sentinel value.
        """
        while True:
            item = await self.ast_tree_queue.get()
            if item is SENTINEL:  # Check for the sentinel
                break
            file_path, ast_tree = item
            test_module = self.parse_ast_tree(file_path, ast_tree)
            if test_module:
                self.test_modules.append(
                    test_module
                )  # Append to a list instead of putting it to a queue
                logger.debug(f"Test module {test_module} has been parsed")
            self.ast_tree_queue.task_done()

    def parse_ast_tree(self, module_name: Path, ast_tree: ast.Module) -> TestModule:
        """Parse an AST into a TestModule object.

        Args:
            module_name: Path to the module.
            ast_tree: The AST of the module.

        Returns:
            The :class: `TestModule` object.
        """
        nodes = list(ast.iter_child_nodes(ast_tree))
        function_nodes = ASTTestModuleFactory.get_function_nodes(nodes)
        test_cases = ASTTestModuleFactory.extract_entities(
            function_nodes, TestCase, ASTTestModuleFactory.is_test_case
        )
        fixtures = ASTTestModuleFactory.extract_entities(
            function_nodes, PytestFixture, ASTTestModuleFactory.is_pytest_fixture
        )
        parsed_test_classes = ASTTestModuleFactory.parse_test_classes(
            ASTTestModuleFactory.get_test_classes(nodes)
        )

        return TestModule(module_name.stem, parsed_test_classes, test_cases, fixtures)


@dataclass
class AsyncASTParser:
    """Parse Python files into TestModule objects.

    This class encapsulates the logic of parsing Python files into TestModule objects.
    It is used in conjunction with ASTProducer and ASTConsumer.

    Parameters:
        file_paths: The paths of the Python files to parse.
        test_modules: The list of TestModule objects produced from the Python files.
    """

    file_paths: List[Path]
    test_modules: List[TestModule] = field(default_factory=list)

    def __post_init__(self):
        """Initialize the class."""
        self.run()

    def __len__(self):
        """Return the number of TestModule objects."""
        amount_test_cases = 0
        for test_module in self.test_modules:
            amount_test_cases += len(test_module)
        return amount_test_cases

    async def run_producer_consumer(self):
        """Run the producer-consumer pattern."""
        async with ASTProducer(self.file_paths) as producer, ASTConsumer(
            producer.ast_tree_queue, self.test_modules
        ) as consumer:
            await producer.task
            await producer.ast_tree_queue.put(SENTINEL)  # Signal consumer to stop
            await consumer.task

    async def gather_producer_consumer_task(self):
        """Gather the producer-consumer task."""
        await asyncio.gather(self.run_producer_consumer())

    def run(self):
        """Run the producer-consumer task."""
        return asyncio.run(self.gather_producer_consumer_task())
