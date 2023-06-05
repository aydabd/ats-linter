============
Introduction
============

Automated Test Schema Linter `ATS-Linter <https://readthedocs.org/projects/ats-linter/>`_.

Description
===========

This project contains library and terminal cli command for linting
test code and test description based on the desired template schema.
ats-linter can be used as an separate terminal CLI or as a configuration for
`pre-commit <https://pre-commit.com/>`_.

This package is available at `pypi <https://pypi.org/project/ast-linter/>`_ and `conda-forge <https://anaconda.org/conda-forge/ast-linter>`_ . T
his ensure the easy installation to your test development environment by `pip`_ or `conda`_.

.. note::

   It is recommended to use an isolated environment as provided by `venv <https://docs.python.org/3/library/venv.html>`_ or
   even better `Anaconda <https://anaconda> for your work with Python in general.

Installation
------------

Make sure virtualenv ``Miniconda`` (`recommended`) activated.
Install with ``pip`` or ``conda``::

   pip install --upgrade ats-linter
   # Or install as conda package(recommended)
   conda install ats-linter

How To Start ats-linter
--------------------------

Check `installation-guide`_.

.. _pip: https://pypi.org/project/pip/ats-linter
.. _conda: https://conda.io/docs/user-guide/install/index.html
.. _installation-guide: :ref:`installation-guide`
