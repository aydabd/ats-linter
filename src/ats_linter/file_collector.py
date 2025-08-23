"""Copyright (c) 2023 Aydin Abdi

This module defines a class for collecting test directories and files.

Example:
    test_directory = FileCollector('/path/to/root/directory')
    print(test_directory.test_directories)
    print(test_directory.test_files)
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import InitVar, asdict, dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from loguru import logger

# Comment out to enable logging
logger.disable(__name__)

# Define constants
TEST_DIRECTORY_PREFIXES = ("test", "test_", "tests")
TEST_FILE_PREFIXES = "test_"
PYTHON_FILE_EXTENSION = ".py"
TEST_FILE_PATTERN = f"{TEST_FILE_PREFIXES[0]}*{PYTHON_FILE_EXTENSION}"
All_RECRUSIVE_PATTERN = "**/"


@dataclass
class FileCollector:
    """Collect test directories and files from a root directory or file.

    Parameters:
        root_file_path: The path of the root directory or file.
        root_path: The root directory as a Path object.
        test_directories: A list of all directories that contain test files.
        test_files: A list of all test files.

    Example:
        test_directory = FileCollector('/path/to/root/directory')
        print(test_directory.test_directories)
        print(test_directory.test_files)
    """

    root_file_path: InitVar[str]
    root_path: Path = field(init=False)
    test_directories: List[Path] = field(default_factory=list, init=False)
    test_files: List[Path] = field(default_factory=list, init=False)

    def __post_init__(self, root_file_path: str):
        """Initialize a FileCollector object.

        If the root_file_path is a file, add it to the test_files list.
        If it is a directory, collect all test directories and files.

        Args:
            root_file_path: The path of the root directory or file.
        """
        self.root_path = FileCollector.get_path_from_string(root_file_path)
        # If the root path does not exist, log an error and return.
        if not self.root_path.exists():
            logger.error(f"Path {self.root_path} does not exist.")
            return
        # If the root path is a file, add it to the test_files list.
        if FileCollector.is_test_file(self.root_path):
            logger.debug(f"Root path is a test file: {self.root_path}")
            self.test_files.append(self.root_path)
        # If the root path is a directory, collect all test directories and files.
        if self.root_path.is_dir():
            logger.debug(f"Root path is a directory: {self.root_path}")
            self.collect_test_directories_and_files_in_parallel()

    def __dict__(self) -> dict:  # type: ignore
        """Return the FileCollector object as a dictionary.

        Returns:
            The FileCollector object as a dictionary.
        """
        return asdict(self)

    def __len__(self) -> int:
        """Return the number of test files.

        Returns:
            The number of test files.

        Example:
            file_collector = FileCollector('/path/to/root/directory')
            print(len(file_collector))
        """
        return len(self.test_files)

    def __iter__(self) -> Iterable[Path]:
        """Return an iterator for the test files.

        Returns:
            An iterator for the test files.

        Example:
            file_collector = FileCollector('/path/to/root/directory')
            for test_file in file_collector:
                print(test_file)
        """
        return iter(self.test_files)

    @staticmethod
    def get_path_from_string(file_path: str) -> Path:
        """Return a Path object for a given file path string.

        Args:
            file_path: The file path as a string.

        Returns:
            The file path as a Path object.
        """
        return Path(file_path)

    @staticmethod
    def is_test_file(file: Path) -> bool:
        """Check if the file is a test file.

        Args:
            file: The file to check.

        Returns:
            True if the file is a test file, False otherwise.
        """
        return (
            file.is_file()
            and file.name.startswith(TEST_DIRECTORY_PREFIXES)
            and file.name.endswith(PYTHON_FILE_EXTENSION)
        )

    @staticmethod
    def process_directory(directory: Path) -> Tuple[Optional[Path], List[Path]]:
        """Process a directory and return it if it is a test directory.
        Args:
            directory: The directory to process.
        Returns:
            A tuple containing the directory and its test files.
        """
        if FileCollector.is_test_directory(directory):
            files = list(directory.glob(TEST_FILE_PATTERN))
            return directory, files
        else:
            return None, []

    @staticmethod
    def is_test_directory(directory: Path) -> bool:
        """Check if the directory is a test directory.

        A directory is considered a test directory if it starts with
        ``test`` or ``test_`` or ``tests`` and contains at least one file that
        starts with ``test_``.

        Args:
            directory: The directory to check.

        Returns:
            True if the directory is a test directory, False otherwise.
        """
        return directory.name.lower().startswith(TEST_DIRECTORY_PREFIXES) and any(
            file.name.startswith(TEST_FILE_PREFIXES) for file in directory.iterdir()
        )

    def collect_test_directories_and_files_in_parallel(self) -> None:
        """Collect all test directories and files in parallel.

        If the root directory is a file, simply add it to the test files and return.
        If the root directory is a directory, collect all test directories and files.
        """
        with ThreadPoolExecutor() as executor:
            # Create a future for each subdirectory.
            futures = [
                executor.submit(self.process_directory, directory)
                for directory in self.root_path.glob(All_RECRUSIVE_PATTERN)
                if directory.is_dir()
            ]

            # Gather results from futures.
            for future in as_completed(futures):
                try:
                    directory, files = future.result()
                    if directory:
                        self.test_directories.append(directory)
                        self.test_files.extend(files)
                except Exception as e:
                    logger.error(f"An exception occurred: {e}")
