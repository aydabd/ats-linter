.. image:: https://github.com/aydabd/ats-linter/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/aydabd/ats-linter/actions/workflows/ci.yml
   :alt: CI Status

.. image:: https://codecov.io/gh/aydabd/ats-linter/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/aydabd/ats-linter
   :alt: Coverage Status

.. image:: https://img.shields.io/pypi/v/ats-linter.svg
   :target: https://pypi.org/project/ats-linter/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/ats-linter.svg
   :target: https://pypi.org/project/ats-linter/
   :alt: Python Versions

.. image:: https://img.shields.io/pypi/dm/ats-linter.svg
   :target: https://pypi.org/project/ats-linter/
   :alt: Monthly Downloads

.. image:: https://img.shields.io/github/license/aydabd/ats-linter.svg
   :target: https://github.com/aydabd/ats-linter/blob/main/LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/code%20style-ruff-000000.svg
   :target: https://github.com/astral-sh/ruff
   :alt: Code Style: Ruff

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: Pre-commit Enabled

.. image:: https://img.shields.io/badge/docs-sphinx-blue.svg
   :target: https://ats-linter.readthedocs.io/
   :alt: Documentation

.. image:: https://img.shields.io/github/repo-size/aydabd/ats-linter.svg
   :target: https://github.com/aydabd/ats-linter
   :alt: Repository Size

.. image:: https://img.shields.io/github/last-commit/aydabd/ats-linter.svg
   :target: https://github.com/aydabd/ats-linter/commits/main
   :alt: Last Commit

.. image:: https://img.shields.io/github/issues/aydabd/ats-linter.svg
   :target: https://github.com/aydabd/ats-linter/issues
   :alt: Open Issues

.. image:: https://img.shields.io/badge/Docker-integrated-blue?logo=docker
   :target: https://github.com/aydabd/ats-linter/tree/main/integration_test
   :alt: Docker Integration

.. image:: https://img.shields.io/badge/CLI-Typer-ff69b4?logo=python
   :target: https://typer.tiangolo.com/
   :alt: Modern CLI with Typer

============
Introduction
============

Automated Test Schema Linter `ATS-Linter`_.

Description
===========

This project contains library and terminal cli command for linting
test code and test description based on the desired template schema.
ats-linter can be used as an separate terminal CLI or as a configuration for
`pre-commit`_.

This package is available at `pypi`_ and `conda-forge`_ . This ensures easy
installation to your test development environment by `pip`_ or `micromamba`_.


Environment Setup
-----------------

It is recommended to use an isolated environment for development. This project uses `micromamba` for fast, reproducible environment management.

To set up the environment:

.. code-block:: bash

   micromamba create -f .githooks.d/pre-commit_environment.yaml
   micromamba activate ats-linter

All dependencies (including test and dev) are specified in `.githooks.d/pre-commit_environment.yaml` and `pyproject.toml`.


Installation
------------

Install from PyPI:

.. code-block:: bash

   pip install --upgrade ats-linter

Or install for development:

.. code-block:: bash

   pip install -r requirements-dev.txt
   pip install -e .


Testing & Linting
-----------------

Run all tests and coverage with tox:

.. code-block:: bash

   tox -e py312
   # or for all configured Python versions
   tox

Lint and style checks:

.. code-block:: bash

   tox -e lint

Build documentation:

.. code-block:: bash

   tox -e docs

Run integration tests (requires Docker):

.. code-block:: bash

   tox -e integration-test


How To Start ats-linter
-----------------------

Check `installation-guide`_.

.. _ATS-Linter : https://ats-linter.readthedocs.io/en/latest/
.. _pypi: https://pypi.org/project/pip/ats-linter
.. _pip: https://pip.pypa.io/en/stable/installing/
.. _venv: https://docs.python.org/3/library/venv.html
.. _installation-guide: https://ats-linter.readthedocs.io/en/latest/
.. _pre-commit: https://pre-commit.com/
.. _conda-forge: https://conda-forge.org/
.. _micromamba: https://mamba.readthedocs.io/en/latest/index.html
