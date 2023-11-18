"""
This is a minimal example on how to retrieve data from water info.
Make sure to set up a path to store the resulting dataframe. Also, decomment
the line of code
"""

from ddlpy import ddlpy
import datetime
import math
import pandas as pd
import os

start_date = datetime.datetime(2023, 10, 1)
end_date = datetime.datetime(2023, 11, 1)
station = 'PORTZLDBSD' # Deventer

seen = []

alfabet = ['A', 'B', 'C', 'D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'] 

for letter in alfabet:
    ref = []
    for link in alfabet:
        if letter == link :
            ref.append(link) 
        else :
            ref.append("[%s](%s)" % (link, "stations_"+ link +".md"))
    f = open("stations_"+ letter +".md", "w")
    f.write(" | ".join(ref))
    f.write("\n\n")
    f.close()

locations = ddlpy.locations()

#locations = locations[locations.index == station]
locations = locations.sort_index()

counter = 0

for index, row in locations.iterrows():
    key = index +"|"+ row["Grootheid.Code"]
    
    if key not in seen :
        seen.append(key)
        letter = key[0]
        #f_counter = math.trunc(counter/100)
        
        #f = open("stations_"+ str(f_counter) +".txt", "a")
        f = open("stations_"+ letter +".md", "a")
        
        print(index +"|"+ row["Grootheid.Code"])
        
        if ddlpy.measurements_available(row, start_date, end_date):
            #f.write("# Actief \n")
            
            if index == "PORTZLDBSD" :
                f.write("station = '"+ index +"\n")
            else:
                f.write("station = '"+ index +"'            # "+ row["Naam"] +"\n")
        
            f.write("code = '"+ row["Grootheid.Code"] +"'            # "+ row["Parameter_Wat_Omschrijving"] +"\n\n")
            f.close()
            counter += 1
