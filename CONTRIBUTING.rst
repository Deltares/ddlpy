.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.


Report Bugs
-----------

Report bugs at https://github.com/deltares/ddlpy/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.


Get Started!
------------

Ready to contribute? Here's how to set up `ddlpy` for local development.

1. Fork the `ddlpy` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/ddlpy.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv ddlpy
    $ cd ddlpy/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ flake8 ddlpy tests
    $ python setup.py test or py.test
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.


Testing
-------

To run all the tests::

$ pytest


To run a subset of tests::

$ pytest tests/test_ddlpy.py


Generate documentation
----------------------

To generate the documentation::

$ sphinx-build docs docs/_build


Create release
--------------

- make sure the ``main`` branch is up to date (check pytest warnings, important issues solved, all pullrequests and branches closed)
- create and checkout branch for release
- bump the versionnumber with ``bumpversion minor``
- update heading (including date) in ``HISTORY.rst``
- run testbank
- local check with: ``python -m build`` and ``twine check dist/*``
- commit+push to branch and merge PR
- copy the ddlpy version from pyproject.toml (e.g. ``0.3.0``)
- create a new release at https://github.com/Deltares/ddlpy/releases/new
- click ``choose a tag`` and type v+versionnumber (e.g. ``v0.3.0``), click ``create new tag on publish``
- set the release title to the tagname (e.g. ``v0.3.0``)
- click ``Generate release notes`` and replace the ``What's Changed`` info by a tagged link to ``HISTORY.rst``
- if all is set, click ``Publish release``
- a release is created and published on PyPI by the github action
- post-release: commit+push ``bumpversion patch`` and ``UNRELEASED`` header in ``HISTORY.rst`` to distinguish between release and dev version
