"""
This is a minimal example on how to retrieve data from the DDL with ddlpy.
"""

import ddlpy
import datetime as dt

# get the dataframe with locations and their available parameters
locations = ddlpy.locations()

#select a set of parameters 
# Filter the locations dataframe with the desired parameters and stations.
bool_stations = locations.index.isin(['ijmuiden.buitenhaven', 'dantziggat.zuid', 'hoekvanholland', 'ameland.nes'])
# meting/astronomisch/verwachting
bool_procestype = locations['ProcesType'].isin(['meting'])
# waterlevel/waterhoogte (WATHTE)
bool_grootheid = locations['Grootheid.Code'].isin(['WATHTE'])
# timeseries (NVT) versus extremes
bool_groepering = locations['Groepering.Code'].isin([''])
# vertical reference (NAP/MSL)
bool_hoedanigheid = locations['Hoedanigheid.Code'].isin(['NAP'])
selected = locations.loc[bool_procestype &
                         bool_stations & bool_grootheid & 
                         bool_groepering & bool_hoedanigheid]

start_date = dt.datetime(2023, 1, 1)
end_date = dt.datetime(2023, 1, 15)

# provide a single row of the locations dataframe to ddlpy.measurements
measurements = ddlpy.measurements(selected.iloc[0], start_date=start_date, end_date=end_date)

if not measurements.empty:
    print('Data was found in RWS Waterwebservices/DDL')
    measurements.plot(y="Meetwaarde.Waarde_Numeriek", linewidth=0.8)
else:
    print('No Data!')
