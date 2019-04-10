# ddlpy
API to Dutch archive of monitoring water data, for Python

See also https://github.com/wstolte/rwsapi for the R API.

Make sure you have installed:

* Pandas

* numpy

To install this code, go to the directory where this code is located andy type in a console:
python setup.py install

In the folder examples you will find the following files:

* minimal exmaple.py -> minimal code to retrieve data from Water Info. 

* 1_get_data_from_water_info_parallel.py -> Code to retrieve a bulk of observations per parameter and per station. 

This code is parallelized; therefore, you can specify the number of processors you want to use.

The output of this code is the data in csv format.

* 2_get_netcdf.py -> Code to transform the csv files run in the previous script into netcdf files. 

More detailed explanation on the usage of these codes are inside the Python files.

