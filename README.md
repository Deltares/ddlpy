# ddlpy

(D)ata (D)istributie (L)aag is a service from Rijkswaterstaat for distributing water quantity data. This package provides an API for python.

[![pypi-image](https://img.shields.io/pypi/v/rws-ddlpy.svg)](https://pypi.python.org/pypi/rws-ddlpy)

[![image](https://img.shields.io/travis/deltares/ddlpy.svg)](https://travis-ci.org/deltares/ddlpy)

[![Documentation Status](https://readthedocs.org/projects/rws-ddlpy/badge/?version=latest)](https://rws-ddlpy.readthedocs.io/en/latest/?badge=latest)

[![Updates](https://pyup.io/repos/github/deltares/ddlpy/shield.svg)](https://pyup.io/repos/github/deltares/ddlpy/)

Service from Rijkswaterstaat for distributing water quantity data.

-   Documentation: <https://ddlpy.readthedocs.io>.

See also https://github.com/wstolte/rwsapi for the R API.


# Install

This text will be updated soon and a new pypi release will also happen soon.
The latest ddlpy PyPI release is outdated, but it can be installed with:

	pip install rws-ddlpy

The newest version is currently installed directly from github with:

    pip install git+https://github.com/deltares/ddlpy

In the folder examples you will find the following files:

* minimal example.py -> minimal code to retrieve data.

* 1_get_data_from_water_info_parallel.py -> Code to retrieve a bulk of observations per parameter and per station.

The output of this code is the data in csv format.

* 2_get_netcdf.py -> Code to transform the csv files run in the previous script into netcdf files.

More detailed explanation on the usage of these codes are inside the `notebooks` directory.

# Run ddlpy from console

You can also run ddlpy from the console. The options you can use are the following:
* Write locations metadata to output file, given input station codes and parameter codes:

    ddlpy locations

To get access to the help menu, type in a terminal: ddlpy locations --help.

* Obtain measurements from json file containing locations and codes:

    ddlpy measurements

To get access to the help menu, type in a terminal: ddlpy measurements --help.

IMPORTANT: You can not run `ddlpy measurements` before running `ddlpy locations`, unless you already have a .json file listing the stations and the parameters you need data from.
