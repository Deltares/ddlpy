"""
This is a minimal example on how to retrieve data from water info.
Make sure to set up a path to store the resulting dataframe. Also, decomment
the line of code
"""

#from ddlpy import ddlpy
import datetime
import matplotlib
import pandas as pd
import os

# get location
locations = ddlpy.locations()

#select a parameter with specific hoede code.
# This should be an input from console
code= 'T'
unit= 'NVT'

# Here we retrieve a dataframe with the desired parameters.
# Note that each index corresponds to one location.
parameter = locations[(locations['Grootheid.Code'] == code) &
                      (locations['Hoedanigheid.Code'] == unit) ]


#parameter = parameter[~parameter.index.duplicated(keep='first')] # remove double index

location= parameter.index[0]
l= parameter.loc[location] # series with the metadata of the location (i.e station)


start_date = datetime.datetime(2000, 1, 1) # also inputs for the code
end_date = datetime.datetime(2005, 3, 1)
measurements = ddlpy.measurements(l, start_date=start_date, end_date=end_date)

if (len(measurements) > 0):
    print('Data was found in Waterbase')
    measurements['locatie_code'] = location

    for name, value in zip(l.index, l.values):
        measurements[name] = value

    #measurements.to_csv(directory+"%s_%s.csv"%(location, donar_parcode), index= False)

else:
    print('No Data!')
