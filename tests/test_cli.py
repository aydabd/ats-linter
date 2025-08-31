import pytest
import typer

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

    with pytest.raises(typer.Exit) as exc_info:
        cli.main()
    assert exc_info.value.exit_code == 0


def test_main_failure(mocker):
    mocker.patch("ats_linter.cli.FileProcessorCocurrent", side_effect=Exception("fail"))
    with pytest.raises(typer.Exit) as exc_info:
        cli.main()
    assert exc_info.value.exit_code == 1


def test_run_calls_main(mocker):
    mock_app = mocker.patch("ats_linter.cli.app")
    cli.run()
    mock_app.assert_called_once()


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

    with pytest.raises(typer.Exit) as exc_info:
        cli.main()
    assert exc_info.value.exit_code == 0  # No test cases found results in exit code 0


def test_main_linting_fails(mocker):
    """Test when linting fails due to invalid test cases."""
    mock_file_processor = mocker.patch("ats_linter.cli.FileProcessorCocurrent")
    mock_test_class = mocker.Mock()
    mock_test_class.test_cases = ["case1"]
    mock_module = mocker.Mock()
    mock_module.test_classes = [mock_test_class]
    mock_module.test_cases = []
    mock_file_processor.return_value.__iter__.return_value = [mock_module]

    mock_factory = mocker.patch("ats_linter.cli.ATSTestCasesFactory")
    mock_factory.return_value.ats_test_cases = ["ats_case1"]
    mock_linter = mocker.patch("ats_linter.cli.ATSTestCasesLinter")
    mock_linter.return_value.lint.return_value = False
    mock_linter.return_value.lint_results = {"ok": False}

    with pytest.raises(typer.Exit) as exc_info:
        cli.main()
    assert exc_info.value.exit_code == 1  # Linting failure results in exit code 1
