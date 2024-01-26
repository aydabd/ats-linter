import pytest
from pathlib import Path

from ats_linter.file_collector import FileCollector


@pytest.fixture
def file_collector(mock_files: Path) -> FileCollector:
    """A pytest fixture that returns a FileCollector object

    initialized with the mock files.
    """
    print("Setup: Initializing a FileCollector object.")
    file_collector = FileCollector(str(mock_files))
    yield file_collector
    # Teardown code goes after the yield
    print("Teardown: Cleaning up after FileCollector.")
    file_collector.test_directories.clear()
    file_collector.test_files.clear()


@pytest.fixture
def mock_files(tmpdir):
    """Mock files and directories for testing."""
    # Create mock directories and files
    root_dir = Path(tmpdir.mkdir("root"))
    test_dir1 = root_dir / "test_dir1"
    test_dir2 = root_dir / "test_dir2"
    non_test_dir = root_dir / "dir3"

    test_dir1.mkdir()
    test_dir2.mkdir()
    non_test_dir.mkdir()

    (test_dir1 / "test_file1.py").touch()
    (test_dir1 / "test_file2.py").touch()
    (test_dir2 / "test_file3.py").touch()
    (non_test_dir / "file4.py").touch()

    return root_dir


@pytest.fixture
def test_directory(tmp_path: Path) -> Path:
    """Create a test directory."""
    test_directory = tmp_path / "test_directory"
    test_directory.mkdir()
    test_file = test_directory / "test_file.py"
    test_file.write_text("print('hello world')")
    yield test_directory
    # Teardown/cleanup code goes here
    for item in test_directory.iterdir():
        item.unlink()
    test_directory.rmdir()


@pytest.fixture
def non_test_directory(tmp_path: Path) -> Path:
    """Create a non-test directory."""
    non_test_directory = tmp_path / "non_test_directory"
    non_test_directory.mkdir()
    non_test_file = non_test_directory / "non_test_file.py"
    non_test_file.write_text("print('hello world')")
    yield non_test_directory
    # Teardown/cleanup code goes here
    for item in non_test_directory.iterdir():
        item.unlink()
    non_test_directory.rmdir()


@pytest.fixture
def non_test_directory_with_test_prefix(tmp_path: Path) -> Path:
    """Creates a directory with a test prefix, but without any test files."""
    non_test_directory_with_test_prefix = tmp_path / "test_directory_without_test_file"
    non_test_directory_with_test_prefix.mkdir()
    non_test_file_in_test_prefix_dir = (
        non_test_directory_with_test_prefix / "non_test_file.py"
    )
    non_test_file_in_test_prefix_dir.write_text("print('hello world')")
    yield non_test_directory_with_test_prefix
    # Teardown/cleanup code goes here
    for item in non_test_directory_with_test_prefix.iterdir():
        item.unlink()
    non_test_directory_with_test_prefix.rmdir()
