# AGENTS.md — Coding Agent Instructions for ats-linter

## Project Overview

**ats-linter** is a Python package for automated test schema linting. It enforces conventions and discoverability for test files and directories, supporting maintainable, high-quality test code. The project is used by developers and CI/CD pipelines.

## Repository Structure

- `src/ats_linter/`: Main source code (file collection, AST parsing, CLI, data classes, etc.)
- `tests/`: Unit and integration tests (pytest-based)
- `docs/`: Sphinx documentation
- `conda_envs/`, `conda-recipe/`: Environment and packaging
- `.github/`: Workflows and Copilot/Codex instructions
- `pyproject.toml`, `tox.ini`, `environment.yaml`: Project configuration

## Environment Setup
- Always use `environment.yaml` with micromamba or conda:
  ```sh
  micromamba create -f environment.yaml
  micromamba activate ats-linter
  ```
- All dependencies (including test/dev) are in `environment.yaml` and `pyproject.toml`.

## Build, Test, Lint, and Docs
- **Test:**
  ```sh
  tox -e py312
  # or for all versions
  tox
  ```
- **Lint:**
  ```sh
  tox -e lint
  ```
- **Docs:**
  ```sh
  tox -e docs
  ```

## Coding Standards
- Follow PEP8, use type hints, docstrings, and idiomatic Python.
- Use pytest for all new tests; tests go in `tests/` and import from `src/ats_linter/`.
- Use Sphinx for documentation.
- Use loguru for logging.

## CI/CD
- GitHub Actions workflow in `.github/workflows/ci.yml` runs lint, tests, build, and publish.
- PyPI and conda-forge publishing is automated on tag push.

## Agent Guidance
- Always activate the micromamba environment before running any build, test, or lint command.
- Use the exact commands above for validation and automation.
- If you add dependencies, update both `environment.yaml` and `pyproject.toml` (and `requirements-dev.txt` if needed).
- Place all new or updated tests in `tests/`, importing code from `src/ats_linter/`.
- Use Sphinx for documentation; build docs with `tox -e docs` and keep docstrings up to date.
- Prefer modern, Pythonic solutions and libraries when implementing new features.
- When in doubt, follow the Zen of Python (`import this`).

## Troubleshooting
- If coverage is 0%, ensure `PYTHONPATH` includes `src` and that tests import code from `src/ats_linter/`.
- If tox or pytest is not found, ensure the micromamba environment is activated.
- If you encounter import errors, check for missing `__init__.py` files and correct import paths.
- If Sphinx docs fail to build, check for missing dependencies or incorrect docstring formatting.
- If CI fails, review `.github/workflows/ci.yml` for the correct sequence and environment setup.

---

These instructions are for OpenAI Codex and other coding agents to ensure efficient, error-free development and automation in this repository.
