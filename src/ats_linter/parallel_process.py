"""Copyright (c) 2023 Aydin Abdi

FileProcessorCocurrent is a class for processing files in parallel.
"""

from dataclasses import asdict, dataclass, field

from loguru import logger

from ats_linter.async_ast_parser import AsyncASTParser
from ats_linter.file_collector import FileCollector


@dataclass
class FileProcessorCocurrent:
    """A class for processing files in parallel."""

    root_path: str
    test_file_collector: FileCollector = field(init=False)
    async_ast_parser: AsyncASTParser = field(init=False)

    def __post_init__(self):
        """Initialize a ParallelProcess object.

        This method collects all MHS test files and parses them in parallel.
        """
        # producer
        self.test_file_collector = FileCollector(self.root_path)
        # consumer and producer
        self.async_ast_parser = AsyncASTParser(self.test_file_collector.test_files)

    def __len__(self):
        total_test_classes = 0

        for test_module in self.async_ast_parser.test_modules:
            total_test_classes += len(test_module.test_classes)

        logger.debug(f"Total amount of test classes: {total_test_classes}")
        logger.debug(f"Total amount of test cases: {len(self.async_ast_parser)}")
        return len(self.async_ast_parser)

    def __iter__(self):
        return iter(self.async_ast_parser.test_modules)

    def __dict__(self):
        return [asdict(m) for m in self.async_ast_parser.test_modules]
