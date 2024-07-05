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
    
    # simplyfy dataframe (drop constant columns and add these properties as attributes)
    simplified = ddlpy.simplify_dataframe(measurements)
    # dropping timezone is required to get proper encoding in time variable (in netcdf file)
    simplified.index = simplified.index.tz_convert(None)
    
    # convert to xarray
    ds = simplified.to_xarray()
    ds = ds.assign_attrs(simplified.attrs)
    
    # write to netcdf file    
    ds.to_netcdf(filename)


if ( __name__ == "__main__" ):
    
    dir_output = './ddl_retrieved_data'
    os.makedirs(dir_output, exist_ok=True)
    
    # get locations
    locations = ddlpy.locations()
    bool_stations = locations.index.isin(['IJMDBTHVN', 'DANTZGZD', 'HOEKVHLD', 'VLISSGN', 'HOEK', 'VLIS', "OLST"])
    bool_grootheid = locations['Grootheid.Code'].isin(['WATHTE']) # measured (WATHTE) versus computed/astro
    bool_groepering = locations['Groepering.Code'].isin(['NVT']) # timeseries (NVT) versus extremes
    bool_hoedanigheid = locations['Hoedanigheid.Code'].isin(['NAP']) # vertical reference (NAP/MSL)
    selected = locations.loc[bool_stations & bool_grootheid & bool_groepering & bool_hoedanigheid]
    
    
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
    ax.legend(loc=1)
