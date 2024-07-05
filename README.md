[![pypi-image](https://img.shields.io/pypi/v/rws-ddlpy.svg)](https://pypi.python.org/pypi/rws-ddlpy)
[![pytest](https://github.com/Deltares/ddlpy/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/Deltares/ddlpy/actions/workflows/pytest.yml)
[![codecov](https://img.shields.io/codecov/c/github/deltares/ddlpy.svg?style=flat-square)](https://app.codecov.io/gh/deltares/ddlpy?displayType=list)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Deltares_ddlpy&metric=alert_status)](https://sonarcloud.io/summary/overall?id=Deltares_ddlpy)
[![Supported versions](https://img.shields.io/pypi/pyversions/rws-ddlpy.svg)](https://pypi.org/project/rws-ddlpy)
[![Downloads](https://img.shields.io/pypi/dm/rws-ddlpy.svg)](https://pypistats.org/packages/rws-ddlpy)

# ddlpy

(D)ata (D)istributie (L)aag is a service from Rijkswaterstaat for distributing water quantity data. This package provides an API for Python. See also https://github.com/wstolte/rwsapi for the R API.


# Install

Install the latest ddlpy PyPI release with (extra dependencies between `[]` are optional):

	pip install rws-ddlpy[netcdf,examples]

# Examples

Documentation: <https://deltares.github.io/ddlpy>

In the examples/notebooks folders you will find the following examples to get you started:

* [minimal_example.py](https://github.com/Deltares/ddlpy/blob/main/docs/examples/minimal_example.py) -> minimal code to retrieve data.

* [retrieve_parallel_to_netcdf.py](https://github.com/Deltares/ddlpy/blob/main/docs/examples/retrieve_parallel_to_netcdf.py) -> Code to retrieve a bulk of observations and write to netcdf files for each station.

* [measurements.ipynb](https://github.com/Deltares/ddlpy/blob/main/docs/notebooks/measurements.ipynb) -> interactive notebook to subset/inspect locations and download/plot measurements

* [waterinfo.ipynb](https://github.com/Deltares/ddlpy/blob/main/docs/notebooks/waterinfo.ipynb) -> interactive notebook to read csv's obained from waterinfo.rws.nl


# Run ddlpy from console

With `ddlpy locations` you can generate a (subsetted) locations.json file, for instance:

	ddlpy locations --quantity WATHTE --station HOEKVHLD

With `ddlpy measurements` you can obtain measurements for locations/parameters in an existing locations.json, for instance:

	ddlpy measurements 2023-01-01 2023-01-03


# Something broke?

Check the [status of the DDL](https://rijkswaterstaatdata.nl/waterdata/#hfd2f5e23-5092-4169-9f36-41e9734e7d87) (at the *Updates* heading). If you have a suggestion or found a bug in ddlpy, please [create an issue](https://github.com/Deltares/ddlpy/issues).
