"""
This script gets data from water info and generates a csv dataframe per location and station.

"""
from ddlpy import ddlpy
import datetime
import matplotlib
import pandas as pd
import numpy as np
import os
import concurrent.futures


def get_data(location, code, parameter, start_date, end_date, directory):

    print ('location:', location)

    try:
        l= parameter.loc[location]
        filename= directory+"%s_%s.csv"%(location, code)

        if (os.path.isfile(filename) is False ): # check that file doesnot exists in the computer.
            measurements = ddlpy.measurements(l, start_date=start_date, end_date=end_date)
            print('number of measurements:', len(measurements))

            if (len(measurements) > 0):
                print('Data was found in Waterinfo')
                measurements['locatie_code'] = location

                for name, value in zip(l.index, l.values):
                    measurements[name] = value

                measurements.to_csv(filename, index= False)

            return location

        else:
            return 'file already exists'

    except:
        return 'failed getting data in {}'.format(location)



if ( __name__ == "__main__" ):
    
    #These are the inputs of the code you need to change. Check excel file parameter_needed to change donar_parcode
    donar_parcode= 'WATHTE' # Donar parcode
    directory = './data_waterlevel/csv_files/' # Should exist this folder

    # Get Noord sea stations
    stations = pd.read_excel("./SeaDataNet_information/locatiesNoordzee.xlsx", usecols= [3])
    stations = list(stations.Code.values)

    #get codes (to do: use codes files instead)
    info= pd.read_excel('./SeaDataNet_information/parameters_needed.xls', skiprows= 14)
    info.set_index('donar_parcode', inplace= True)


    # get location
    locations = ddlpy.locations()
    
    # Get table of parameters
    gcode= info.loc[donar_parcode, 'Aquo_Grootheid_code']

    if (donar_parcode == 'WATHTE'):
        hoedaniheid_code = input('Introduce the Aquo_Hoedanigheid_code:')
        gcode= donar_parcode
    
    if (gcode == 'CONCTTE'):
        parameter = locations[(locations['Grootheid.Code'] == gcode)  &
                              (locations['Hoedanigheid.Code'] == info.loc[donar_parcode, 'Aquo_Hoedanigheid_code'] ) &
                              (locations['Parameter.Code'] == donar_parcode )
                ]
    
    elif (gcode == 'WATHTE'):
        parameter = locations[(locations['Grootheid.Code'] == gcode)  &
                              (locations['Hoedanigheid.Code'] == hoedaniheid_code) 
                 ]
    
    else:
        parameter = locations[(locations['Grootheid.Code'] == gcode)  &
                              (locations['Hoedanigheid.Code'] == info.loc[donar_parcode, 'Aquo_Hoedanigheid_code'] ) 
                 ]

    start_date = datetime.datetime(1956, 1, 1)
    end_date = datetime.datetime(2019, 3, 1)

    # Parallelization. It uses 3 processors. Customable parameter.
    with concurrent.futures.ProcessPoolExecutor(max_workers= 3) as executor:
        futures = [
            executor.submit(
                get_data,
                location,
                donar_parcode,
                parameter,
                start_date,
                end_date,
                directory
                ) for location in stations]

    print([future.result() for future in futures])
