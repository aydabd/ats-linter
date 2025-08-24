***UNDER CONSTRUCTION***

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
installation to your test development environment by `pip`_ or `conda`_.

.. note::

   It is recommended to use an isolated environment as provided by `venv`_ or
   even better `Miniconda`_ for your work with Python in general.

Installation
------------

Make sure virtualenv ``Miniconda`` (`recommended`) activated.
Install with ``pip`` or ``conda``::

   pip install --upgrade ats-linter
   # Or install as conda package(recommended)
   conda install ats-linter

For development, install additional requirements and the package in editable mode::

   pip install -r requirements-dev.txt
   pip install -e .


How To Start ats-linter
-----------------------

Check `installation-guide`_.

.. _ATS-Linter : https://ats-linter.readthedocs.io/en/latest/
.. _pypi: https://pypi.org/project/pip/ats-linter
.. _pip: https://pip.pypa.io/en/stable/installing/
.. _conda-forge: https://anaconda.org/conda-forge/ats-linter
.. _conda: https://conda.io/projects/conda/en/stable/user-guide/install/index.html
.. _venv: https://docs.python.org/3/library/venv.html
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _installation-guide: https://ats-linter.readthedocs.io/en/latest/
.. _pre-commit: https://pre-commit.com/
