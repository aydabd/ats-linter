"""Copyright (c) 2023 Aydin Abdi

Cli is the command line interface for the linter.
"""
from loguru import logger

from ats_linter.linter import ATSTestCasesLinter
from ats_linter.parallel_process import FileProcessorCocurrent

# Uncomment this line to enable debug logging.
# logger.enable("ats_linter")

FILE_PATH = "tests/"


def main():
    """The main routine."""
    logger.debug("Running the linter...")

    try:
        file_processor = FileProcessorCocurrent(FILE_PATH)
    except Exception as e:
        logger.error(f"Error parsing file: {e.with_traceback()}")
        return False

    lint_status = ATSTestCasesLinter.lint(file_processor)
    logger.debug(f"Lint status: {lint_status}")
    status = all(lint_status.values())
    if not status:
        logger.info(f"Test case docstrings are valid. {lint_status}")
        return False

    logger.error("Some test case docstrings are invalid.")
    return True


def run():
    main()


if __name__ == "__main__":
    run()
