"""Copyright (c) 2023 Aydin Abdi

Ats-linter(Automated Test Schema Linter) is a package for linting test files.
It is a tool that checks the validity of test case docstrings and
test code based on the defined schema.
It is designed to be used in a CI/CD pipeline to ensure
that test cases are written according to the defined schema.
It is also designed to be used as a standalone tool to lint test files locally.
It is built on top of Python's AST (Abstract Syntax Tree).
It can be used as a pre-commit hook.

Example:
    To lint test files locally, run the following command:

    .. code-block:: console

        $ ats-linter --path tests/

    To lint test files in a CI/CD pipeline, run the following command:

    .. code-block:: console

        $ ats-linter --path tests/ --output junit.xml

        The junit.xml file can be used to generate a report in Jenkins.

    To lint test files in a CI/CD pipeline, run the following command:

    .. code-block:: console

        $ ats-linter --path tests/ --output junit.xml

        The junit.xml file can be used to generate a report in Jenkins.

"""

from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "ats-linter"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
