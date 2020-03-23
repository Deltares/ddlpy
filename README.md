# ddlpy

(D)ata (D)istributie (L)aag is a service from Rijkswaterstaat for distributing water quantity data. This package provides an API for python.

[![pypi-image](https://img.shields.io/pypi/v/ddlpy.svg)](https://pypi.python.org/pypi/ddlpy)

[![image](https://img.shields.io/travis/openearth/ddlpy.svg)](https://travis-ci.org/openearth/ddlpy)

[![Documentation Status](https://readthedocs.org/projects/ddlpy/badge/?version=latest)](https://ddlpy.readthedocs.io/en/latest/?badge=latest)

[![Updates](https://pyup.io/repos/github/openearth/ddlpy/shield.svg)](https://pyup.io/repos/github/openearth/ddlpy/)

Service from Rijkswaterstaat for distributing water quantity data.

-   Free software: GNU General Public License v3
-   Documentation: <https://ddlpy.readthedocs.io>.


See also https://github.com/wstolte/rwsapi for the R API.


# Install
Make sure you have installed:

* pandas
* numpy
* click
* python-dateutil>=2.8

To install this ddlpy, go to the directory where this code is located and type in a console:

    pip install ddlpy

In the folder examples you will find the following files:

* minimal example.py -> minimal code to retrieve data.

* 1_get_data_from_water_info_parallel.py -> Code to retrieve a bulk of observations per parameter and per station.

This code is parallelized; therefore, you can specify the number of processors you want to use.

The output of this code is the data in csv format.

* 2_get_netcdf.py -> Code to transform the csv files run in the previous script into netcdf files.

More detailed explanation on the usage of these codes are inside the `notebooks` directory.

# Run ddlpy from console

You can also run ddlpy from the console. The options you can use are the following:
	  
	ddlpy locations:  Write locations metadata to output file, given input codes. To get access to the help menu, type in a termnal: ddlpy locations --help

	ddlpy measurements: Obtain measurements from file with locations and codes. To get access to the help menu, type in a terminal: ddlpy measurements --help


