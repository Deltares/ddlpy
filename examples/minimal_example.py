"""
This is a minimal example on how to retrieve data from water info.
Make sure to set up a path to store the resulting dataframe. Also, decomment
the line of code
"""

from ddlpy import ddlpy
import datetime
import matplotlib
import pandas as pd
import os


# get all locations
locations = ddlpy.locations()

#select a set of parameters 
# and a set of stations
code= 'WATHTE'
unit= 'NAP'
station= ['IJMDBTHVN', 'DANTZGZD','HOEKVHLD' ]

# Filter the locations dataframe with the desired parameters and stations.
selected= locations[locations.index.isin(station)]

selected = selected[(selected['Grootheid.Code'] == code) &
                      (selected['Hoedanigheid.Code'] == unit) ].reset_index()

# Obtain measurements per parameter row
index= 1
location= selected.loc[index]

start_date = datetime.datetime(2015, 1, 1) # also inputs for the code
end_date = datetime.datetime(2015, 12, 31)
measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)

if (len(measurements) > 0):
    print('Data was found in Waterbase')
    #measurements.to_csv("%s_%s_%s.csv"%(location.Code, code, unit), index= False)
else:
    print('No Data!')

    
    
    
    
    
