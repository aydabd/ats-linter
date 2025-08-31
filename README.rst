.. image:: https://github.com/aydabd/ats-linter/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/aydabd/ats-linter/actions/workflows/ci.yml
   :alt: CI Status

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
