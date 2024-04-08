# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 20:28:44 2024

@author: veenstra
"""

import ddlpy
import xarray as xr

locations = ddlpy.locations()
bool_hoedanigheid = locations['Hoedanigheid.Code'].isin(['NAP'])
bool_stations = locations.index.isin(['BAALHK'])
bool_grootheid = locations['Grootheid.Code'].isin(['WATHTE'])
bool_groepering = locations['Groepering.Code'].isin(['NVT'])
selected = locations.loc[bool_grootheid & bool_hoedanigheid & bool_groepering & bool_stations]

# VLISSING has different WaardeBepalingsmethode from 1-2-2024
date_start = "1990-01-15"
date_end = "1990-01-19"

measurements = ddlpy.measurements(selected.iloc[0], date_start, date_end)
print(measurements['WaardeBepalingsmethode.Code'].drop_duplicates())

# simple = ddlpy.simplify_dataframe(measurements)

# some actions on dataframe
colname_code_list = measurements.columns[measurements.columns.str.contains(".Code")]
colname_list = colname_code_list.str.replace(".Code","")
# colname_oms_list = colname_list+".Omschrijving"

# create var_attrs_dict
var_attrs_dict = {}
for colname in colname_list:
    colname_code = f"{colname}.Code"
    colname_oms = f"{colname}.Omschrijving"
    meas_twocol = measurements[[colname_code,colname_oms]].drop_duplicates()
    attr_dict = meas_twocol.set_index(colname_code)[colname_oms].to_dict()
    var_attrs_dict[colname_code] = attr_dict

# to_xarray
ds1 = measurements.to_xarray()
# ds2 = simple.to_xarray()

def dataframe_to_xarray(df, keep=[]):

    # create lists of bulky columns (duplicate info), all-NVT columns and location columns
    cols_bulky = ["AquoMetadata_MessageID", "Parameter_Wat_Omschrijving"]
    if "Meetwaarde.Waarde_Alfanumeriek" in df.columns and 'Meetwaarde.Waarde_Numeriek' in df.columns:
        # drop alfanumeriek if duplicate of numeriek # TODO: should not be returned by ddl
        cols_bulky.append("Meetwaarde.Waarde_Alfanumeriek")
    bool_onlynvt_code = (df=='NVT').all(axis=0) #TODO: can this be aligned with above?
    bool_onlynvt_oms = ((df=='Niet van toepassing').all(axis=0) | (df=='Waarde is niet van toepassing').all(axis=0)) #TODO: can these be aligned
    cols_onlynvt_code = df.columns[bool_onlynvt_code].tolist()
    cols_onlynvt_oms = df.columns[bool_onlynvt_oms].tolist()
    cols_location = ['Code', 'Naam', 'Coordinatenstelsel', 'X', 'Y']
    
    attrs_columns = cols_onlynvt_code + cols_location
    ds_attrs = {k:df[k].iloc[0] for k in attrs_columns}
    
    drop_columns = cols_bulky + cols_onlynvt_code + cols_onlynvt_oms + cols_location
    df_simple = df.drop(drop_columns, axis=1, errors='ignore')
    
    colname_code_list = df_simple.columns[df_simple.columns.str.contains(".Code")]
    colname_oms_list = colname_code_list.str.replace(".Code",".Omschrijving")

    # drop the timezone to please xarray and convert to xarray
    # TODO: this raises "ValueError: invalid time units: 1970-01-01 00:00:00 +01:00"
    # tz = df_simple.index.tz
    # assert str(tz) == 'UTC+01:00'
    # tz_offset = str(tz).replace("UTC","")
    # df_simple.index = df_simple.index.tz_localize(None)
    # ds = df_simple.to_xarray()
    # # update encoding manually with timezone
    # ds.time.encoding['units'] = f"1970-01-01 00:00:00 {tz_offset}"
    
    # convert to UTC to please xarray and convert to xarray
    df_simple.index = df_simple.index.tz_convert(None)
    ds = df_simple.to_xarray()
    
    # drop *.Omschrijving columns
    ds = ds.drop_vars(colname_oms_list)

    # assign attrs with code+omschrijving to each variable
    for varn in ds.data_vars:
        if varn in var_attrs_dict.keys():
            var_attrs = var_attrs_dict[varn]
            ds[varn] = ds[varn].assign_attrs(var_attrs)

    ds = ds.assign_attrs(ds_attrs)
    return ds

ds3 = dataframe_to_xarray(measurements)
# ds3["WaardeBepalingsmethode.Omschrijving"] = xr.DataArray(measurements["WaardeBepalingsmethode.Omschrijving"].values, dims='time')
ds3 = ds3.drop_vars(["WaarnemingMetadata.OpdrachtgevendeInstantieLijst",
                     "WaarnemingMetadata.BemonsteringshoogteLijst",
                     ],errors="ignore")

# TODO: convert retrieved meas-types to attrs (since they are always all constant)
# Compartiment.Code
# Eenheid.Code
# Grootheid.Code
# Hoedanigheid.Code (?)
# BemonsteringsSoort.Code (?)

ds3.to_netcdf("file_nc.nc")
ds_file = xr.open_dataset("file_nc.nc")

print(f'full [MB]: {ds1.nbytes/1024**2:.3f}')
# print(f'simple [MB]: {ds2.nbytes/1024**2:.3f}')
print(f'filt [MB]: {ds3.nbytes/1024**2:.3f}')
print(f'file [MB]: {ds_file.nbytes/1024**2:.3f}')

