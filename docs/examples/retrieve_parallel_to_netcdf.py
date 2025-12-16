"""
This script gets data from ddl on multiple cores and generates a netcdf file per location and station.

"""
import ddlpy
import datetime as dt
import matplotlib.pyplot as plt
plt.close("all")
import xarray as xr
import os
from concurrent.futures import ProcessPoolExecutor
import glob

# enabling debug logging so we can see what happens in the background
import logging
logging.basicConfig()
logging.getLogger("ddlpy").setLevel(logging.DEBUG)


def get_data(location, start_date, end_date, dir_output, overwrite=True):
    station_id = location.name
    station_messageid = location["Locatie_MessageID"]
    filename = os.path.join(dir_output, f"{station_id}-{station_messageid}.nc")
    
    if os.path.isfile(filename) and overwrite is False:
        print('{station_id}: netcdf file already exists and overwrite=False, skipping')
        return
    
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    
    if measurements.empty:
        print(f'{station_id}: no measurements found')
        return

    print(f'{station_id}: writing retrieved data to netcdf file')
    
    # convert to xarray: constant columns are converted to attributes to save disk space, except the columns in always_preserve
    always_preserve = [
        'WaarnemingMetadata.Statuswaarde',
        'WaarnemingMetadata.Kwaliteitswaardecode',
        'WaardeBepalingsMethode.Code',
        'Meetwaarde.Waarde_Numeriek',
        ]
    ds = ddlpy.dataframe_to_xarray(measurements, always_preserve=always_preserve)
    
    # write to netcdf file. NETCDF3_CLASSIC or NETCDF4_CLASSIC automatically converts 
    # variables of dtype <U to |S which saves a lot of disk space
    ds.to_netcdf(filename, format="NETCDF4_CLASSIC")


if __name__ == "__main__":
    dir_output = './ddl_retrieved_data'
    os.makedirs(dir_output, exist_ok=True)
    
    # get locations
    locations = ddlpy.locations()
    bool_stations = locations.index.isin(['ijmuiden.buitenhaven', 'dantziggat.zuid', 'hoekvanholland', 'ameland.nes', 'vlissingen', 'olst'])
    bool_procestype = locations['ProcesType'].isin(['meting']) # meting/astronomisch/verwachting
    bool_grootheid = locations['Grootheid.Code'].isin(['WATHTE']) # waterlevel (WATHTE)
    bool_groepering = locations['Groepering.Code'].isin(['']) # timeseries (NVT) versus extremes
    bool_hoedanigheid = locations['Hoedanigheid.Code'].isin(['NAP']) # vertical reference (NAP/MSL)
    selected = locations.loc[bool_stations & bool_procestype & bool_grootheid & bool_groepering & bool_hoedanigheid]
    
    start_date = dt.datetime(2022, 1, 1)
    end_date = dt.datetime(2022, 3, 1)
    
    # normal code
    # for station_code, location in selected.iterrows():
    #     get_data(location, start_date, end_date, dir_output)
    
    # parallel code
    with ProcessPoolExecutor(max_workers=3) as executor:
        for station_code, location in selected.iterrows():
            executor.submit(get_data, location, start_date, end_date, dir_output)

    file_list = glob.glob(os.path.join(dir_output, "*.nc"))
    fig, ax = plt.subplots()
    for file_nc in file_list:
        ds = xr.open_dataset(file_nc)
        station_code = ds.attrs["Code"]
        station_naam = ds.attrs["Naam"]
        ds["Meetwaarde.Waarde_Numeriek"].plot(ax=ax, label=f"{station_code} ({station_naam})")
        ds.close()
    ax.legend(loc=1)
