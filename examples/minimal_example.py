"""
This is a minimal example on how to retrieve data from the DDL with ddlpy.
"""

from ddlpy import ddlpy
import datetime as dt

# get all locations
locations = ddlpy.locations()

#select a set of parameters 
# Filter the locations dataframe with the desired parameters and stations.
bool_stations = locations.index.isin(['IJMDBTHVN', 'DANTZGZD','HOEKVHLD'])
# measured (WATHTE) versus computed/astro
bool_grootheid = locations['Grootheid.Code'].isin(['WATHTE'])
# timeseries (NVT) versus extremes
bool_groepering = locations['Groepering.Code'].isin(['NVT'])
# vertical reference (NAP/MSL)
bool_hoedanigheid = locations['Hoedanigheid.Code'].isin(['NAP'])
selected = locations.loc[bool_stations & bool_grootheid & 
                         bool_groepering & bool_hoedanigheid]

# Obtain measurements per parameter row
index = 1
location = selected.reset_index().iloc[index]

start_date = dt.datetime(2015, 1, 1) # also inputs for the code
end_date = dt.datetime(2015, 6, 1)
measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)

if (len(measurements) > 0):
    print('Data was found in Waterbase')
    #measurements.to_csv("%s_%s_%s.csv"%(location.Code, code, unit), index= False)
    measurements.plot(y="Meetwaarde.Waarde_Numeriek")
else:
    print('No Data!')
