"""
This is a minimal example on how to retrieve data from water info.
Make sure to set up a path to store the resulting dataframe. Also, decomment
the line of code
"""

import ddlpy2
import datetime
import pandas as pd
import os

#select a set of parameters 
# and a set of stations
station = 'DEVE' # Deventer
code = 'WATHTE' # Waterhoogte Oppervlaktewater t.o.v. Normaal Amsterdams Peil in cm

loc_filename = "waterinfo_%s_%s.csv"%(station.lower(), code.lower())

# get all locations
# if previous saved : load for quicker acces
if os.path.isfile(loc_filename):
    selected = pd.read_csv (loc_filename)
else :
    locations = ddlpy2.locations()

    # Filter the locations dataframe with the desired parameters and stations.
    selected= locations[locations.index == station]

    selected = selected[(selected['Grootheid.Code'] == code)].reset_index()
    selected.to_csv(loc_filename)

# Obtain measurements per parameter row
index= 0
location= selected.loc[index]

observation = ddlpy2.last_observation(location)
if 'Meetwaarde.Waarde_Numeriek' in observation.columns:
    meetwaarde = observation['Meetwaarde.Waarde_Numeriek'][0]
else:
    meetwaarde = observation['Meetwaarde.Waarde_Alfanumeriek'][0]
    
tijd = observation['Tijdstip'][0]
eenheid = observation['Eenheid.code'][0]

print ("%s %s om %s" % (meetwaarde, eenheid, tijd))

