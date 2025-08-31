"""Copyright (c) 2023 Aydin Abdi.

CLI for the Automated Test Schema Linter (ATS Linter).
Modern, typed, and Pythonic using Typer.
"""

import sys
from typing import Annotated

import typer
from colorama import just_fix_windows_console
from loguru import logger

from ats_linter.linter import ATSTestCasesFactory, ATSTestCasesLinter
from ats_linter.parallel_process import FileProcessorCocurrent

# Force loguru to always colorize output, even in Docker
logger.remove()
logger.add(sys.stderr, colorize=True)

app = typer.Typer(help="ATS Linter: Lint your test files for docstring compliance.")


def _process_files(files_to_process: list[str]) -> list:
    """Process files and extract test cases."""
    test_cases = []
    for file_path in files_to_process:
        try:
            file_processor = FileProcessorCocurrent(file_path)
            for module in file_processor:
                logger.debug(f"Module: {getattr(module, 'file_path', repr(module))}")
                for test_class in module.test_classes:
                    logger.debug(f"  TestClass: {test_class.name}")
                    test_cases.extend(test_class.test_cases)
                test_cases.extend(module.test_cases)
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            raise typer.Exit(code=1) from e
    return test_cases


@app.command()
def main(
    files: Annotated[
        list[str],
        typer.Argument(help="Files or directories to lint (default: tests/ directory)"),
    ] = None,
    debug: Annotated[
        bool, typer.Option("--debug", help="Enable debug logging")
    ] = False,
) -> None:
    """Lint test files for docstring compliance.

    Args:
        files: Files or directories to lint (default: tests/ directory)
        debug: Enable debug logging

    """
    just_fix_windows_console()

    # Configure logging
    if debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", colorize=True)
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO", colorize=True)

    # Determine files to process
    files_to_process = files if files else ["tests/"]
    logger.debug(f"Linting files: {files_to_process}")

    # Process files and extract test cases
    test_cases = _process_files(files_to_process)

    if not test_cases:
        logger.warning("No test cases found to lint.")
        raise typer.Exit(code=0)

    # Run linter
    ats_cases = ATSTestCasesFactory(test_cases).ats_test_cases
    linter = ATSTestCasesLinter(ats_cases)
    status = linter.lint()

    # Report results
    if status:
        logger.opt(colors=True).success(
            "\n<green><b>Automated Test Schema Linter: PASSED</b></green>"
        )
        raise typer.Exit(code=0)
    else:
        logger.opt(colors=True).error(
            "\n<red><b>Automated Test Schema Linter: FAILED</b></red>"
        )
        raise typer.Exit(code=1)


def run() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    run()
