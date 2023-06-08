from ats_linter.file_collector import FileCollector, PYTHON_FILE_EXTENSION
from pathlib import Path


def test_post_init(file_collector: FileCollector, tmp_path) -> None:
    """
    Test that the __post_init__ method correctly initializes a FileCollector.
    """
    expected_test_files = 3
    expected_test_directories = 2
    assert len(file_collector.test_files) == expected_test_files
    assert len(file_collector.test_directories) == expected_test_directories

    test_file = tmp_path / "test_file.py"
    test_file.write_text("print('hello world')")

    file_collector = FileCollector(str(test_file))

    assert len(file_collector.test_files) == 1
    assert file_collector.test_files[0] == test_file


def test_get_path_from_string() -> None:
    """
    Test that the get_path_from_string method correctly
    converts a string path to a Path object.
    """
    input_path_string = "test_path"
    path = FileCollector.get_path_from_string(input_path_string)
    expected_path = Path(input_path_string)
    assert isinstance(path, Path)
    assert path == expected_path


def test_is_test_file(mock_files: Path) -> None:
    """
    Test that the is_test_file method correctly identifies test files.
    """
    test_file = mock_files / "test_dir1" / "test_file1.py"
    non_test_file = mock_files / "dir3" / "file4.py"
    assert FileCollector.is_test_file(test_file) is True
    assert FileCollector.is_test_file(non_test_file) is False


def test_is_test_directory(
    test_directory: Path,
    non_test_directory: Path,
    non_test_directory_with_test_prefix: Path,
) -> None:
    """
    Test the `is_test_directory` method of the `FileCollector` class.
    """
    # Check if the test directory is recognized as a test directory
    assert FileCollector.is_test_directory(test_directory)

    # Check if the non-test directory is recognized as a non-test directory
    assert not FileCollector.is_test_directory(non_test_directory)

    # Check if the directory with test prefix
    # but without any test file is recognized as a non-test directory
    assert not FileCollector.is_test_directory(non_test_directory_with_test_prefix)


def test_process_directory(mock_files: Path) -> None:
    """
    Test that the process_directory method correctly processes
    a directory and returns it if it is a test directory.
    """
    test_dir = mock_files / "test_dir1"
    non_test_dir = mock_files / "dir3"
    expected_test_dir_result = (
        test_dir,
        list(test_dir.glob(f"*{PYTHON_FILE_EXTENSION}")),
    )
    expected_non_test_dir_result = (None, [])
    assert FileCollector.process_directory(test_dir) == expected_test_dir_result
    assert FileCollector.process_directory(non_test_dir) == expected_non_test_dir_result


def test_collect_test_directories_and_files_in_parallel(
    mocker, mock_files: Path, file_collector: FileCollector
) -> None:
    """
    Test that the collect_test_directories_and_files_in_parallel method correctly
    collects all test directories and files in parallel.
    """
    expected_directory_files = [
        (
            mock_files / "test_dir1",
            [
                mock_files / "test_dir1" / "test_file1.py",
                mock_files / "test_dir1" / "test_file2.py",
            ],
        ),
        (mock_files / "test_dir2", [mock_files / "test_dir2" / "test_file3.py"]),
        (None, []),
    ]
    mocker.patch.object(
        FileCollector, "process_directory", side_effect=expected_directory_files
    )

    # Reset test_files before collecting
    file_collector.test_files = []
    file_collector.test_directories = []

    file_collector.collect_test_directories_and_files_in_parallel()

    expected_test_files = 3
    expected_test_directories = 2
    assert len(file_collector) == expected_test_files
    assert len(file_collector.test_directories) == expected_test_directories


def test_len(file_collector: FileCollector) -> None:
    """
    Test that the __len__ method correctly returns the number of test files.
    """
    expected_length = 3
    assert len(file_collector) == expected_length


def test_iter(file_collector: FileCollector) -> None:
    """
    Test that the __iter__ method correctly returns an iterator for the test files.
    """
    expected_files = file_collector.test_files
    assert list(file_collector) == expected_files


def test_root_file_path_is_file(file_collector: FileCollector) -> None:
    """
    Test when the root_file_path is a file.
    """
    assert len(file_collector.test_files) == 3


def test_root_file_path_does_not_exist() -> None:
    """
    Test when the root_file_path does not exist.
    """
    fc = FileCollector("non_existent_path")
    assert len(fc.test_files) == 0


# def test_non_existing_path():
#     collector = FileCollector("non_existing_path")
#     assert len(collector.test_files) == 0
#     assert len(collector.test_directories) == 0

# def test_root_path_is_file():
#     # Assuming 'some_file.py' exists and is not a test file
#     collector = FileCollector("some_file.py")
#     assert len(collector.test_files) == 0
#     assert len(collector.test_directories) == 0

# def test_iteration_over_collector():
#     collector = FileCollector("path_to_test_directory")
#     files = list(collector)
#     assert len(files) == len(collector.test_files)

# def test_exception_during_collection(mocker):
#     mocker.patch.object(Path, "is_dir", side_effect=Exception("Mock Exception"))
#     collector = FileCollector("path_to_test_directory")
#     assert len(collector.test_files) == 0
#     assert len(collector.test_directories) == 0


def test_dict_method(file_collector: FileCollector):
    """Test the __dict__ method."""
    assert isinstance(file_collector.__dict__(), dict)
