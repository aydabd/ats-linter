import pytest
from ats_linter import cli


def test_main_success(mocker):
    mock_file_processor = mocker.patch("ats_linter.cli.FileProcessorCocurrent")
    mock_test_class = mocker.Mock()
    mock_test_class.test_cases = ["case1", "case2"]
    mock_module = mocker.Mock()
    mock_module.test_classes = [mock_test_class]
    mock_module.test_cases = ["case3"]
    mock_file_processor.return_value.__iter__.return_value = [mock_module]

    mock_factory = mocker.patch("ats_linter.cli.ATSTestCasesFactory")
    mock_factory.return_value.ats_test_cases = ["ats_case1", "ats_case2", "ats_case3"]
    mock_linter = mocker.patch("ats_linter.cli.ATSTestCasesLinter")
    mock_linter.return_value.lint.return_value = True
    mock_linter.return_value.lint_results = {"ok": True}

    assert cli.main() is True


def test_main_failure(mocker):
    mock_file_processor = mocker.patch("ats_linter.cli.FileProcessorCocurrent", side_effect=Exception("fail"))
    assert cli.main() is False


def test_run_calls_main(mocker):
    mock_main = mocker.patch("ats_linter.cli.main", return_value=True)
    cli.run()
    mock_main.assert_called_once()


def test_main_lint_failure(mocker):
    mock_file_processor = mocker.patch("ats_linter.cli.FileProcessorCocurrent")
    mock_test_class = mocker.Mock()
    mock_test_class.test_cases = []
    mock_module = mocker.Mock()
    mock_module.test_classes = [mock_test_class]
    mock_module.test_cases = []
    mock_file_processor.return_value.__iter__.return_value = [mock_module]

    mock_factory = mocker.patch("ats_linter.cli.ATSTestCasesFactory")
    mock_factory.return_value.ats_test_cases = []
    mock_linter = mocker.patch("ats_linter.cli.ATSTestCasesLinter")
    mock_linter.return_value.lint.return_value = False
    mock_linter.return_value.lint_results = {"ok": False}

    assert cli.main() is False
