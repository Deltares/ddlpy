# Contributing

With the following steps you can install ddlpy as a developer so you have access to latest version on github and can make changes to the code.

## Install

First, install Pixi: https://pixi.prefix.dev/latest/installation

Then, clone the ddlpy ``git`` repo from https://github.com/Deltares/ddlpy, then navigate into the code folder (where the pyproject.toml is located):
```
git clone https://github.com/Deltares/ddlpy.git
cd ddlpy
```

If git is not recognized as a command, first install Git from https://git-scm.com/install. VSCode and PyCharm should be bundled with a git extension so a manual installation is not always necessary.

Then, create and activate a new pixi environment. This includes a developers installation of ddlpy and the default environment as specified in pyproject.toml:

```
pixi install
```

Any other environments will be installed/updated when you use them for instance when running the tests.

## Running the tests

Running the tests can be done within any of the environment specified in the pyproject.toml (defaults to `default`):

```
pixi run -e default test
```

## Updating the lockfile

If you add any dependencies or change anything in the package configuration, you have to update the lockfile. This is also done (if needed) when running other pixi commands:

```
pixi lock
```

## Generating the docs

Generating the docs is added as a pixi task, which executes sphinx-build:

```
pixi run docs-build
```

## Report bugs

Report bugs at https://github.com/deltares/ddlpy/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

## Contributing

- open an existing issue or create a new issue at https://github.com/Deltares/ddlpy/issues
- create a branch via `Development` on the right. This branch is now linked to the issue and the issue will be closed once the branch is merged with main again
- alternatively fork the repository and do your edits there
- open git bash window in local ddlpy folder (e.g. `C:\DATA\ddlpy`)
- `git fetch origin` followed by `git checkout [branchname]`
- make your local changes to the ddlpy code (including docstrings and unittests for functions), after each subtask do `git commit -am 'description of what you did'` (`-am` adds all changed files to the commit)
- check if all edits were committed with `git status`, if there are new files created also do `git add [path-to-file]` and commit again
- `git push` to push your committed changes your branch on github
- open a pull request at the branch on github, there you can see what you just pushed and the automated checks will show up (testbank and code quality analysis).
- optionally make additional local changes (+commit+push) untill you are done with the issue and the automated checks have passed
- update `docs/whats-new.md` if there are any changes that are relevant to users (added features or bug fixes)
- request a review on the pull request
- after review, squash+merge the branch into main

## Increase the version number

- commit all changes via git
- `pixi run bumpversion major` (or `minor` or `patch`) (changes version numbers in files and commits changes)
- push changes with `git push` (from git bash window/terminal)

## Create release

- make sure the `main` branch is up to date (check pytest warnings, important issues solved, all pullrequests and branches closed)
- create and checkout branch for release
- bump the versionnumber with `pixi run bumpversion minor`
- update the lockfile with `pixi lock`
- update `HISTORY.rst` and with a version+date header for this release (also preserve the `UNRELEASED` header for future PR's)
- run local testbank with `pixi run test`
- local check with: `pixi run python -m build` and `pixi run twine check dist/*` ([does not work on WCF?](https://github.com/pypa/setuptools/issues/4133))
- commit+push to branch and merge PR
- copy the ddlpy version from https://github.com/Deltares/ddlpy/blob/main/pyproject.toml (e.g. `0.11.0`)
- create a [new release](https://github.com/Deltares/ddlpy/releases/new)
- click `choose a tag` and type v+versionnumber (e.g. `v0.11.0`), click `create new tag: v0.11.0 on publish`
- set the release title to the tagname (e.g. `v0.11.0`)
- click `Generate release notes` and replace the `What's Changed` info by a tagged link to `HISTORY.rst`
- if all is set, click `Publish release`
- a release is created and the github action publishes it [on PyPI](https://pypi.org/project/rws-ddlpy)
