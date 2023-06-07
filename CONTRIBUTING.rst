============
Contributing
============

Welcome to ``ats-linter`` contributor's guide.

This document focuses on getting any potential contributor familiarized
with the development processes, but `other kinds of contributions`_ are also
appreciated.

If you are new to using git_ or have never collaborated in a project previously,
please have a look at `contribution-guide.org`_. Other resources are also
listed in the excellent `guide created by FreeCodeCamp`_ [#contrib1]_.

Please notice, all users and contributors are expected to be **open,
considerate, reasonable, and respectful**. When in doubt, `Python Software
Foundation's Code of Conduct`_ is a good reference in terms of behavior
guidelines.


Issue Reports
=============

If you experience bugs or general issues with ``ats-linter``, please have a look
on the `issue tracker`_. If you don't see anything useful there, please feel
free to fire an issue report.

.. tip::
   Please don't forget to include the closed issues in your search.
   Sometimes a solution was already reported, and the problem is considered
   **solved**.

New issue reports should include information about your programming environment
(e.g., operating system, Python version) and steps to reproduce the problem.
Please try also to simplify the reproduction steps to a very minimal example
that still illustrates the problem you are facing. By removing other factors,
you help us to identify the root cause of the issue.


Documentation Improvements
==========================

You can help improve ``ats-linter`` docs by making them more readable and coherent, or
by adding missing information and correcting mistakes.

``ats-linter`` documentation uses Sphinx_ as its main documentation compiler.
This means that the docs are kept in the same repository as the project code, and
that any documentation update is done in the same way was a code contribution.

.. tip:: markup language used:

    reStructuredText_

.. tip::
  Please notice that the `GitHub web interface`_ provides a quick way of
  propose changes in ``ats-linter``'s files. While this mechanism can
  be tricky for normal code contributions, it works perfectly fine for
  contributing to the docs, and can be quite handy.

  If you are interested in trying this method out, please navigate to
  the ``docs`` folder in the source `repository`_, find which file you
  would like to propose changes and click in the little pencil icon at the
  top, to open `GitHub's code editor`_. Once you finish editing the file,
  please write a message in the form at the bottom of the page describing
  which changes have you made and what are the motivations behind them and
  submit your proposal.

When working on documentation changes in your local machine, you can
compile them using |tox|_::

    tox -e docs

and use Python's built-in web server for a preview in your web browser
(``http://localhost:8000``)::

    python3 -m http.server --directory 'docs/_build/html'


Code Contributions
==================


   Objects shall be implemented with facade pattern,
   so that the user can use the same interface to interact with different objects.

Submit an issue
---------------

Before you work on any non-trivial code contribution it's best to first create
a report in the `issue tracker`_ to start a discussion on the subject.
This often provides additional considerations and avoids unnecessary work.

Create an environment
---------------------

#. Before you start coding we recommend to install `Miniconda_Linux`_ or `Miniconda_Windows`_
   which allows to setup a dedicated development environment. For installation of Miniconda,
   get the Linux or Windows installer for ``python latests 64-bit`` from `Miniconda`_ then::

    bash Miniconda3-latest-Linux-x86_64.sh

   or for ``Windows`` just double-click the ``.exe`` file and follow the instructions on the screen.
   For fast installation on linux use these commands,
   for more info check
   `miniconda installation guide <https://conda.io/projects/conda/en/stable/user-guide/install/index.html>`_::

    curl 'https://repo.anaconda.com/miniconda/Miniconda-latest-Linux-x86_64.sh' > Miniconda.sh
    bash Miniconda.sh

   and follow the wizard and update conda at the end::

    conda update conda


#. Now you have a base miniconda environment on your terminal which can be used to create other dev-environments.
#. Remove auto_activate_base and report_errors for your terminal::

    conda config --set auto_activate_base false
    conda config --set report_errors false

#. Add and set default conda channel `all-conda` from artifactory::

    conda config --set channel_alias https://artifactory.se.axis.com/artifactory/api/conda
    conda config --add channels all-conda
    conda config --add default_channels https://artifactory.se.axis.com/artifactory/api/conda/all-conda

#. To make sure all installation for pip installs from axis artifactory::

    pip config set global.index-url https://artifacts.se.axis.com/artifactory/api/pypi/all-pypi/simple


#. Create an environment with the name ``ats-linter-dev``.
   We use the defined configuration file `dev_env.yml`_ at project's conda_envs::

    conda env create -f conda_envs/dev_env.yml

   This list shall be always updated by new packages which the project needed.

#. Now activate the isolated environment::

    conda activate ats-linter-dev

#. Verify that the environment was installed correctly::

    conda env list

   or use ``conda info --envs``

#. For installing new package::

    conda install -c conda-forge <name of the package>

.. Note::

   If you already have Miniconda or anaconda installed, and you just want to upgrade, you should not use the installer.
   Just use ``conda update conda``.

#. For updating entire conda environment, deactivate then update as follow::

    conda deactivate
    conda env update ats-linter-dev --file conda_envs/dev_env.yml
    conda update -n ats-linter-dev --all

   Then you can activate and work with environment as before.

#. You can remove the specified environment by this and start a fresh one to continue::

    conda remove -p $HOME/miniconda3/envs/ats-linter-env --all

#. Uninstalling miniconda for ``Linux``::

    rm -rf ~/miniconda ~/.conda ~/.condarc ~/.continum

   for ``Windows`` go to add/remove program and find Python X.X(Miniconda) to remove.


Clone the repository
--------------------

#. Create an user account on |the repository service| if you do not already have one.
#. Fork the project `repository`_: click on the *Fork* button near the top of the
   page. This creates a copy of the code under your account on |the repository service|.
#. Clone this copy to your local disk::

    git clone git@github.com:YOURLOGIN/ats-linter.git
    cd ats-linter

#. You should run::

    pip install -U pip setuptools -e .

   to be able to import the package under development in the Python REPL.


#. Run |pre-commit|_::

    tox -e lint

   ``ats-linter`` comes with a lot of hooks configured to automatically help the
   developer to check the code being written.

Implement your changes
----------------------

#. Create a branch to hold your changes::

    git checkout -b my-feature

   and start making changes. Never work on the main branch!

#. Start your work on this branch. Don't forget to add docstrings_ to new
   functions, modules and classes, especially if they are part of public APIs.

#. Add yourself to the list of contributors in ``AUTHORS.rst``.

#. When you're done editing, do::

    git add <MODIFIED FILES>
    git commit

   to record your changes in git_.

   Please make sure to see the validation messages from |pre-commit|_ and fix
   any eventual issues.
   This should automatically use flake8_/black_ to check/fix the code style
   in a way that is compatible with the project.

   .. important:: Don't forget to add unit tests and documentation in case your
      contribution adds an additional feature and is not just a bugfix.

      Moreover, writing a `descriptive commit message`_ is highly recommended.
      In case of doubt, you can check the commit history with::

         git log --graph --decorate --pretty=oneline --abbrev-commit --all

      to look for recurring communication patterns.

#. Please check that your changes don't break any unit tests with::

    tox

   (inside the conda `dev_env` environment).

   You can also use |tox|_ to run several other pre-configured tasks in the
   repository. Try ``tox -av`` to see a list of the available checks.

Submit your contribution
------------------------

#. If everything works fine, push your local branch to |the repository service| with::

    git push -u origin my-feature

#. Go to the web page of your fork and click |contribute button|
   to send your changes for review.

#. Find more detailed information in `creating a PR`_. You might also want to open
   the PR as a draft first and mark it as ready for review after the feedbacks
   from the continuous integration (CI) system or any required fixes.


Troubleshooting
===============

The following tips can be used when facing problems to build or test the
package:

#. Most of the troubles are environment issues which can be easily fix by cleaning and then try again.
   Clean up all folders with::

    tox -e clean

   then try again and see if you get errors or not.

.. Warning::

   Do not run ``project_cleaner.py`` script in another folder than project root, it may cause deleting important files on your system.

#. `Pytest can drop you`_ in an interactive session in the case an error occurs.
   In order to do that you need to pass a ``--pdb`` option (for example by
   running ``tox -- -k <NAME OF THE FALLING TEST> --pdb``).
   You can also setup breakpoints manually instead of using the ``--pdb`` option.


Maintainer tasks
================

Releases
--------

If you are part of the group of maintainers and have correct user permissions
on PyPI_, the following steps can be used to release a new version for
``ats-linter``:

#. Make sure all unit tests are successful.
#. Tag the current commit on the main branch with a release tag, e.g., ``1.2.3``.
#. Push the new tag to the upstream repository_, e.g., ``git push upstream 1.2.3``
#. Wait for the CI system to build and test the new tag.
#. Github actions will automatically publish the new version on PyPI_ and conda-forge_.



.. [#contrib1] Even though, these resources focus on open source projects and
   communities, the general ideas behind collaborating with other developers
   to collectively create software are general and can be applied to all sorts
   of environments, including private companies and proprietary code bases.



.. |the repository service| replace:: GitHub
.. |contribute button| replace:: "Create pull request"

.. _repository: https://github.com/aydabd/ats-linter
.. _issue tracker: https://github.com/aydabd/ats-linter/issues


.. |pre-commit| replace:: ``pre-commit``
.. |tox| replace:: ``tox``


.. _black: https://pypi.org/project/black/
.. _contribution-guide.org: https://www.contribution-guide.org/
.. _conda-forge: https://conda-forge.org
.. _creating a PR: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request
.. _dev_env.yml: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file
.. _descriptive commit message: https://chris.beams.io/posts/git-commit
.. _docstrings: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
.. _first-contributions tutorial: https://github.com/firstcontributions/first-contributions
.. _flake8: https://flake8.pycqa.org/en/stable/
.. _git: https://git-scm.com
.. _GitHub's fork and pull request workflow: https://guides.github.com/activities/forking/
.. _guide created by FreeCodeCamp: https://github.com/FreeCodeCamp/how-to-contribute-to-open-source
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _Miniconda_Linux: https://conda.io/projects/conda/en/latest/user-guide/install/linux.html
.. _Miniconda_Windows: https://conda.io/projects/conda/en/latest/user-guide/install/windows.html
.. _other kinds of contributions: https://opensource.guide/how-to-contribute
.. _pre-commit: https://pre-commit.com/
.. _PyPI: https://pypi.org/
.. _PyScaffold's contributor's guide: https://pyscaffold.org/en/stable/contributing.html
.. _Pytest can drop you: https://docs.pytest.org/en/stable/how-to/failures.html#using-python-library-pdb-with-pytest
.. _Python Software Foundation's Code of Conduct: https://www.python.org/psf/conduct/
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/en/stable/
.. _virtual environment: https://realpython.com/python-virtual-environments-a-primer/

.. _GitHub web interface: https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files
.. _GitHub's code editor: https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files
