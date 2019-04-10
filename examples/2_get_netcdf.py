"""
Script to transform csv files into netcdf.
You can run frist the script: 1_get_date_from_water_info_parallel
"""

import matplotlib
import pandas as pd
import numpy as np
import netCDF4 as nc
from netCDF4 import num2date, date2num
from pyproj import Proj, transform
from dateutil.parser import parse
import glob

def get_coordinates(df):
    # values and metadata input system:
    x = np.unique(df.X.values)[0]
    y = np.unique(df.Y.values)[0]
    # transformation to lat, long, metadata of system
    inProj  = Proj("+init=EPSG:25831", preserve_units=True)
    outProj = Proj("+init=EPSG:4326")

    long, lat= transform(inProj,outProj,x,y)
    return x, y, long, lat


class netCDFFile():
    
    def __init__(self, data, codes, donar_parcode, path):
        self.data = data  #csv file. It must be clean!!!! 
        self.codes = codes # already with the parcode as index!!!
        self.donar_parcode= donar_parcode # use sufix of data filename
        self.netcdf_data= nc.Dataset(path+'id%s-%s-%s.nc'%(self.data['Locatie_MessageID'].values[0], self.data['locatie_code'].values[0], self.donar_parcode), 'w')
        
        self.X, self.Y, self.LNG, self.LAT = get_coordinates(self.data)
        
        
    def create_dimensions(self):
        self.netcdf_data.createDimension('location', 1)
        self.netcdf_data.createDimension('time', len(self.data.Tijdstip))
       
    def create_location_variable(self):
        station= self.netcdf_data.createVariable('location', 'S1', ('location'))
        station.long_name = self.data['Naam'].values[0]
        station.name_code = self.data['locatie_code'].values[0]
        station.id = self.data['Locatie_MessageID'].values[0] 
     
    def create_time_variable(self):
        dates= [parse(i) for i in self.data.Tijdstip.astype(str)]

        times = self.netcdf_data.createVariable('time', np.float64, ('time'), fill_value='NaN')
        times.long_name= 'time'
        times.units= 'days since 1970-01-01 00:00' #"days since 1970-01-01 00:00:00 +01:00"
        times.standard_name= "time"
        times.calendar = 'gregorian'
        times[:] = date2num(dates, units = times.units, calendar = times.calendar)
        
    def create_xyx_variables(self):
        x= self.netcdf_data.createVariable('x', np.float64, ('location'))
        x.long_name = "station x"
        x.units = "m"
        x.standard_name = "projection_x_coordinate"
        x.grid_mapping = "epsg"
        x[:] = self.X

        y= self.netcdf_data.createVariable('y', np.float64,  ('location'))
        y.long_name = "station y"
        y.units = "m"
        y.standard_name = "projection_y_coordinate"
        y.grid_mapping = "epsg"
        y[:] = self.Y 

        z= self.netcdf_data.createVariable('z', np.float64,  ('location', 'time'), fill_value='NaN')
        z.long_name = "station depth"
        z.units = "m"
        z.standard_name = "Sampling height "
        z.positive = "up"
        z[:] = np.reshape(self.data['WaarnemingMetadata.BemonsteringshoogteLijst'].values , (1, self.data.shape[0]))

    def create_lat_lng_variables(self):   
        lat= self.netcdf_data.createVariable('latitude', np.float64,  ('location'))
        lat.long_name = "station latitude"
        lat.units = "degrees_north"
        lat.standard_name = "latitude"
        lat.grid_mapping = "wgs84"
        lat[:] = self.LAT

        long= self.netcdf_data.createVariable('longitude', np.float64,  ('location') )
        long.long_name = "station longitude"
        long.units = "degrees_east"
        long.standard_name = "longitude"
        long.grid_mapping = "wgs84"
        long[:] = self.LNG 

    def create_sysref_variables(self):
        epsg= self.netcdf_data.createVariable('epsg', np.int)
        epsg.Name =  "ETRS89 / UTM zone 31N"
        epsg.EPSG_code = "EPSG:%s"%str(dataset.Coordinatenstelsel.unique()[0])
        epsg.center_coordinates_X = 1025504.24
        epsg.center_coordinates_Y = 6522633.24
        epsg.Inferior_Projected_bound_X = -1300111.74
        epsg.Inferior_Projected_bound_Y = 3804640.43
        epsg.Superior_Projected_bound_X = 893164.13
        epsg.Superior_Projected_bound_Y = 9478718.31
        epsg.Method = 'Geocentric translations (geog2D domain)'
        epsg.projection_name =  "m"
        epsg.units = "X Y"
        epsg.comment = "Europe - onshore and offshore , accuracy 1.0 m, code 1149"

        wgs84= self.netcdf_data.createVariable('wgs84', np.int)
        wgs84.Name = "WGS 84"
        wgs84.EPSG_code = "EPSG:4326"
        wgs84.grid_mapping_name = "latitude_longitude"
        wgs84.semi_major_axis =  6378137.0
        wgs84.semi_minor_axis = 6356752.314247833
        wgs84.inverse_flattening = 298.2572236
        wgs84.proj4_params = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs "
        wgs84.projection_name = "Latitude Longitude"
        wgs84.wkt = ""
        wgs84.comment =  "value is equal to EPSG code"
    
    def create_variable_interest(self):
        variable= self.netcdf_data.createVariable(self.codes.loc[self.donar_parcode, 'standard_name'], np.float64, ('location', 'time'), fill_value='NaN') 

        variable.long_name = self.codes.loc[self.donar_parcode, 'long_name']  
        variable.maximum_value= self.data[self.data['Meetwaarde.Waarde_Numeriek'].notnull()]['Meetwaarde.Waarde_Numeriek'].max()
        variable.minimum_value = self.data[self.data['Meetwaarde.Waarde_Numeriek'].notnull()]['Meetwaarde.Waarde_Numeriek'].min()
        variable.units = self.data['Eenheid.Code'].values[0]
        variable.standard_name = self.codes.loc[self.donar_parcode, 'standard_name'] 
        variable.suggested_standard_name= self.codes.loc[self.donar_parcode, 'standard_name'] 
        variable.donar_units = self.codes.loc[self.donar_parcode,'donar_units']
        variable.donar_parcode = self.donar_parcode
        variable.Aquo_Grootheid_code = self.data['Grootheid.Code'].values[0]
        variable.Aquo_Grootheid_omschrijving = self.data['Grootheid.Omschrijving'].values[0]
        variable.Aquo_ChemischeStof_code = self.data['Parameter.Code'].values[0]
        variable.Aquo_ChemischeStof_omschrijving = self.data['Parameter.Omschrijving'].values[0]
        variable.Aquo_CASnummer= self.codes.loc[self.donar_parcode, 'Aquo_CASnummer'] 
        variable.Aquo_Object_code = self.codes.loc[self.donar_parcode, 'Aquo_Object_code'] 
        variable.Aquo_Object_omschrijving = self.codes.loc[self.donar_parcode, 'Aquo_Object_omschrijving'] 
        variable.Aquo_Eenheid_code = self.data['Eenheid.Code'].values[0]
        variable.Aquo_Eenheid_omschrijving = self.data['Eenheid.Omschrijving'].values[0]
        variable.Aquo_Hoedanigheid_code = self.data['Hoedanigheid.Code'].values[0]
        variable.Aquo_Hoedanigheid_omschrijving = self.data['Hoedanigheid.Omschrijving'].values[0]
        variable.Aquo_Compartiment_code = self.data['Compartiment.Code'].values[0]
        variable.Aquo_Compartiment_omschrijving = self.data['Compartiment.Omschrijving'].values[0]
        variable.Aquo_WNS_code = self.codes.loc[self.donar_parcode, 'Aquo_WNS_code'] 
        variable.sdn_standard_name_p02 = self.codes.loc[self.donar_parcode, 'sdn_standard_name'] 
        variable.sdn_prefLabel_p01 = self.codes.loc[self.donar_parcode, 'sdn_prefLabel'] 
        variable.sdn_units_p06 = self.codes.loc[self.donar_parcode, 'sdn_units'] 
        variable[:] = np.reshape(self.data['WaarnemingMetadata.BemonsteringshoogteLijst'].values, (1, self.data.shape[0]))
        
    def general_attributes(self):
        self.netcdf_data.institution = 'Rijkswaterstaat'
        self.netcdf_data.references= '<https://waterinfo.rws.nl/#!/nav/expert/>,<http://openearth.deltares.nl>'
        self.netcdf_data.email= '<servicedesk-data@rws.nl>'
        self.netcdf_data.comment= "The structure of this netCDF file is described in: https://cf-pcmdi.llnl.gov/trac/wiki/PointObservationConventions, http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.5/cf-conventions.html#id2867470"
        self.netcdf_data.version= ""
        self.netcdf_data.conventions= "CF-1.6, UM Aquo 2010 proof of concept, SeaDataNet proof of concept"
        self.netcdf_data.featureType = "timeSeries"
        self.netcdf_data.terms_for_use = "These data can be used freely for research purposes provided that the following source is acknowledged: Rijkswaterstaat."
        self.netcdf_data.disclaimer= "This data is made available in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."
        self.netcdf_data.stationname= self.data['Naam'].values[0]
        self.netcdf_data.location= self.data['Naam'].values[0]

        self.netcdf_data.geospatial_lat_min = self.LAT
        self.netcdf_data.geospatial_lat_max = self.LAT
        self.netcdf_data.geospatial_lon_min = self.LNG
        self.netcdf_data.geospatial_lon_max = self.LNG
        self.netcdf_data.time_coverage_start = str(self.data.Tijdstip.min())
        self.netcdf_data.time_coverage_end = str(self.data.Tijdstip.max())
        self.netcdf_data.geospatial_lat_units = "degrees_north"
        self.netcdf_data.geospatial_lon_units = "degrees_east"
        
    def create_netcdf_file(self):
        self.create_dimensions()
        self.create_location_variable()
        self.create_time_variable()
        self.create_xyx_variables()
        self.create_lat_lng_variables()
        self.create_sysref_variables()
        self.create_variable_interest()
        self.general_attributes()
        
        self.netcdf_data.close()
        
#################################################        
#################### main #######################
#################################################

# There are the inputs of the code that you need to change.
ipath = './data_chlorophyl/csv_files/'
opath=  './data_chlorophyl/netcdf_files/'

# get all the csv filenames
files = glob.glob(ipath+'*.csv')

# read file with codes
codes =  pd.read_excel('./SeaDataNet_information/codes.xlsx')
codes.set_index('donar_parcode', inplace= True)

# Process to get netcdf files
for i in range(len(files)):
    print (i, files[i])
    filename = files[i][len(ipath):]
    donar_parcode= filename[:-4].split('_')[1]

    dataset = pd.read_csv(ipath+filename)

    #Cleaning of the dataset
    dataset.Tijdstip = pd.to_datetime(dataset.Tijdstip, utc= True).dt.tz_convert(tz= None) # convert to UTC and removes timezone offset
    dataset = dataset.sort_values(by= 'Tijdstip', ascending= True)
    dataset.dropna(inplace= True) # try to solve this? Frequency of observations is not constant over time.

    # convert this columns into numerical
    numcols= ['Meetwaarde.Waarde_Numeriek', 'WaarnemingMetadata.BemonsteringshoogteLijst']
    dataset[numcols] = dataset[numcols].astype(float)
    dataset.replace([99999, 9999, 999, -999999999], [np.nan, np.nan, np.nan, np.nan], inplace= True)

    # get netcdf file
    netfile = netCDFFile(dataset, codes, donar_parcode, opath)
    netfile.create_netcdf_file()







