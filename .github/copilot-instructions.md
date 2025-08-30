# Copilot Repository Instructions for ats-linter

## Project Overview

**ats-linter** is a Python package for automated test schema linting. It helps ensure test files and directories follow conventions and are easy to discover and validate. The project is intended for developers and CI/CD pipelines to maintain high-quality, well-structured test code.

## Folder Structure

- `/src/ats_linter/`: Main source code (modules: file collection, AST parsing, CLI, data classes, etc.)
- `/tests/`: Unit and integration tests for all modules
- `/docs/`: Documentation (Sphinx)
- `/conda_envs/`, `/conda-recipe/`: Environment and packaging
- `.github/`: GitHub workflows and Copilot instructions
- `pyproject.toml`, `tox.ini`, `environment.yaml`: Project configuration

## Build, Test, and Validation Steps

### Environment Setup
- Always use the provided `environment.yaml` with micromamba or conda:
  ```sh
  micromamba create -f environment.yaml
  micromamba activate ats-linter
  ```
- All dependencies (including test and dev) are specified in `environment.yaml` and `pyproject.toml`.

### Running Tests
- Use tox for all test and coverage tasks:
  ```sh
  tox -e py312
  # or for all configured Python versions
  tox
  ```
- Tests are in the `tests/` directory and use pytest (with xdist, cov, mock, fixture-config).
- Coverage is measured for `src/ats_linter/`.

### Linting and Docs
- Lint and style checks:
  ```sh
  tox -e lint
  ```
- Build documentation:
  ```sh
  tox -e docs
  ```

### CI/CD
- GitHub Actions workflow in `.github/workflows/ci.yml` runs lint, tests, build, and publish steps.
- PyPI and conda-forge publishing is automated on tag push.


## Coding Standards & Pythonic Best Practices
- Follow [PEP8](https://peps.python.org/pep-0008/) for code style and formatting.
- Use [type hints](https://docs.python.org/3/library/typing.html) throughout all code and tests.
- Write clear, complete [docstrings](https://peps.python.org/pep-0257/) for all public modules, classes, and functions.
- Prefer list comprehensions, generator expressions, and idiomatic Python constructs over manual loops where appropriate.
- Use context managers (`with` statements) for file and resource management.
- Avoid code duplication; refactor common logic into functions or classes.
- Use f-strings for string formatting.
- Handle exceptions explicitly and log errors using the `loguru` library.
- Organize tests as `test_*.py` in the `tests/` directory, and use fixtures for setup/teardown.
- Write small, focused functions and keep classes single-responsibility.
- Use `__all__` in modules to define public API where appropriate.
- Prefer absolute imports within the package.
- Use `pytest` for all new tests; avoid mixing with `unittest` unless required for legacy reasons.
- Use parameterized tests for repetitive logic.


## Key Notes for Copilot
- Always activate the micromamba environment before running any build, test, or lint command.
- Use the exact commands above for validation and automation.
- If you add dependencies, update both `environment.yaml` and `pyproject.toml` (and `requirements-dev.txt` if needed).
- Place all new or updated tests in `tests/`, importing code from `src/ats_linter/`.
- Use Sphinx for documentation; build docs with `tox -e docs` and keep docstrings up to date.
- Prefer modern, Pythonic solutions and libraries when implementing new features.
- When in doubt, follow the Zen of Python (`import this`).


## Known Issues & Workarounds
- If coverage is 0%, ensure `PYTHONPATH` includes `src` and that tests import code from `src/ats_linter/`.
- If tox or pytest is not found, ensure the micromamba environment is activated.
- If you encounter import errors, check for missing `__init__.py` files and correct import paths.
- If Sphinx docs fail to build, check for missing dependencies or incorrect docstring formatting.
- If CI fails, review `.github/workflows/ci.yml` for the correct sequence and environment setup.

---

These instructions are for Copilot and contributors to ensure efficient, error-free development and automation in this repository.
