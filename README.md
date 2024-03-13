[![pypi-image](https://img.shields.io/pypi/v/ddlpy.svg)](https://pypi.python.org/pypi/ddlpy)
[![pytest](https://github.com/Deltares/ddlpy/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/Deltares/ddlpy/actions/workflows/pytest.yml)
[![codecov](https://img.shields.io/codecov/c/github/deltares/ddlpy.svg?style=flat-square)](https://app.codecov.io/gh/deltares/ddlpy?displayType=list)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Deltares_ddlpy&metric=alert_status)](https://sonarcloud.io/summary/overall?id=Deltares_ddlpy)
[![Supported versions](https://img.shields.io/pypi/pyversions/ddlpy.svg)](https://pypi.org/project/ddlpy)
[![Downloads](https://img.shields.io/pypi/dm/ddlpy.svg)](https://pypistats.org/packages/ddlpy)

# ddlpy

(D)ata (D)istributie (L)aag is a service from Rijkswaterstaat for distributing water quantity data. This package provides an API for python.

Documentation: <https://deltares.github.io/ddlpy>

See also https://github.com/wstolte/rwsapi for the R API.


# Install

If you had ddlpy installed before please uninstall since the package was renamed on PyPI:

	pip uninstall rws-ddlpy -y

Install the latest ddlpy PyPI release with:

	pip install ddlpy

In the examples/notebooks folders you will find the following files:

* `examples/minimal example.py` -> minimal code to retrieve data.

* `examples/retrieve_parallel_to_netcdf.py` -> Code to retrieve a bulk of observations and write to netcdf files for each station.

* `notebooks/measurements.ipynb` -> interactive notebook to subset/inspect locations and download/plot measurements

* `notebooks/waterinfo.ipynb` -> interactive notebook to read csv's obained from waterinfo.rws.nl


# Run ddlpy from console

You can also run ddlpy from the console. With `ddlpy locations` you can generate a (subsetted) locations.json file, for instance:

	ddlpy locations --quantity WATHTE --station HOEKVHLD

To get access to the help menu, type: `ddlpy locations --help`.

With `ddlpy measurements` you can obtain measurements for locations/parameters in an existing locations.json:

	ddlpy measurements 2023-01-01 2023-01-03

To get access to the help menu, type: `ddlpy measurements --help`.
