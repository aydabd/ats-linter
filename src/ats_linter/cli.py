"""Copyright (c) 2023 Aydin Abdi.

Cli is the command line interface for the linter.
"""

from loguru import logger

from ats_linter.linter import ATSTestCasesFactory, ATSTestCasesLinter
from ats_linter.parallel_process import FileProcessorCocurrent

# Uncomment this line to enable debug logging.
# logger.enable("ats_linter")

FILE_PATH = "tests/"


def main():
    """Run main."""
    logger.debug("Running the linter...")

    try:
        file_processor = FileProcessorCocurrent(FILE_PATH)
    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        return False

    test_cases = []
    for module in file_processor:
        for test_class in module.test_classes:
            test_cases.extend(test_class.test_cases)
        test_cases.extend(module.test_cases)

    ats_cases = ATSTestCasesFactory(test_cases).ats_test_cases
    linter = ATSTestCasesLinter(ats_cases)
    status = linter.lint()
    logger.debug(f"Lint results: {linter.lint_results}")

    if status:
        logger.info("Test case docstrings are valid.")
    else:
        logger.error("Some test case docstrings are invalid.")

    return status


def run():
    """Run the linter."""
    main()


if __name__ == "__main__":
    run()
