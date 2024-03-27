# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 20:28:44 2024

@author: veenstra
"""

import ddlpy

locations = ddlpy.locations()
bool_hoedanigheid = locations['Hoedanigheid.Code'].isin(['NAP'])
bool_stations = locations.index.isin(['BAALHK'])
bool_grootheid = locations['Grootheid.Code'].isin(['WATHTE'])
bool_groepering = locations['Groepering.Code'].isin(['NVT'])
selected = locations.loc[bool_grootheid & bool_hoedanigheid & bool_groepering & bool_stations]

# TODO: how to get this from a measurements dataframe? Might be more useful to decide on 
# >> a list of important properties that are kept, but this is case specific
catalog_filter = ['Compartimenten','Eenheden','Grootheden',
                  'Hoedanigheden','Groeperingen','MeetApparaten',
                  'Typeringen','WaardeBepalingsmethoden','Parameters']
locations_extended = ddlpy.locations(catalog_filter=catalog_filter)
bool_hoedanigheid = locations_extended['Hoedanigheid.Code'].isin(['NAP'])
bool_stations = locations_extended.index.isin(['BAALHK'])
bool_grootheid = locations_extended['Grootheid.Code'].isin(['WATHTE'])
bool_groepering = locations_extended['Groepering.Code'].isin(['NVT'])
selected_extended = locations_extended.loc[bool_grootheid & bool_hoedanigheid & bool_groepering & bool_stations]

# VLISSING has different WaardeBepalingsmethode from 1-2-2024
date_start = "1990-01-15"
date_end = "1990-05-15"

measurements = ddlpy.measurements(selected.iloc[0], date_start, date_end)
print(measurements['WaardeBepalingsmethode.Code'].drop_duplicates())

simple = ddlpy.simplify_dataframe(measurements)
# TODO: somehow the column AquoMetadata_MessageID does not have constant values

# some actions on dataframe
colname_code_list = measurements.columns[measurements.columns.str.contains(".Code")]
colname_list = colname_code_list.str.replace(".Code","")
colname_oms_list = colname_list+".Omschrijving"

# create var_attrs_dict
# TODO: deside whether to derive attrs from measurements dataframe or from extended locations dataframe
var_attrs_dict = {}
for colname in colname_list:
    colname_code = f"{colname}.Code"
    colname_oms = f"{colname}.Omschrijving"
    if 1: # from measurements (=all keys)
        meas_twocol = measurements[[colname_code,colname_oms]].drop_duplicates()
    else: # from extended locations (=all values)
        if colname_code not in selected_extended.columns:
            continue
        meas_twocol = selected_extended[[colname_code,colname_oms]].drop_duplicates()
    attr_dict = meas_twocol.set_index(colname_code)[colname_oms].to_dict()
    var_attrs_dict[colname] = attr_dict


# to_xarray
ds1 = measurements.to_xarray()
ds2 = simple.to_xarray()

def dataframe_to_xarray(df, keep=[]):
    
    # drop alfanumeriek if duplicate of numeriek # TODO: should not be returned by ddl
    if "Meetwaarde.Waarde_Alfanumeriek" in df.columns and 'Meetwaarde.Waarde_Numeriek' in df.columns:
        df = df.drop("Meetwaarde.Waarde_Alfanumeriek", axis=1)

    # simplify dataframe but re-add some columns #TODO: put this copy in the simplify function
    df_simple = ddlpy.simplify_dataframe(df).copy()
    keep_list = ["WaarnemingMetadata.KwaliteitswaardecodeLijst",
                 "WaarnemingMetadata.StatuswaardeLijst"]
    for colname in keep_list:
        if colname in df.columns:
            df_simple[colname] = df[colname]
    
    colname_code_list = df_simple.columns[df_simple.columns.str.contains(".Code")]
    colname_list = colname_code_list.str.replace(".Code","")
    colname_oms_list = colname_list+".Omschrijving"
    
    # drop the timezone to please xarray and convert to xarray
    df_simple.index = df_simple.index.tz_convert(None)
    ds = df_simple.to_xarray()
    
    # drop *.Omschrijving columns
    ds = ds.drop_vars(colname_oms_list)
    
    # drop *.Code suffix #TODO: maybe avoid this
    # drop_code_prefix_dict = {k:v for k,v in zip(colname_code_list, colname_list)}
    # ds = ds.rename_vars(drop_code_prefix_dict)

    # assign attrs with code+omschrijving to each variable
    for varn in ds.data_vars:
        if varn in var_attrs_dict.keys():
            var_attrs = var_attrs_dict[varn]
            ds[varn] = ds[varn].assign_attrs(var_attrs)
    
    # drop prefixes in other dot variables #TODO: maybe avoid this
    # for varn in ds.data_vars:
    #     if "." in varn:
    #         varn_short = varn.split(".")[1]
    #         ds = ds.rename_vars({varn:varn_short})
    return ds

ds3 = dataframe_to_xarray(measurements)
ds3 = ds3.drop_vars(["WaarnemingMetadata.OpdrachtgevendeInstantieLijst",
                     "AquoMetadata_MessageID"],errors="ignore")

print(f'full [MB]: {ds1.nbytes/1024**2:.3f}')
print(f'simple [MB]: {ds2.nbytes/1024**2:.3f}')
print(f'filt [MB]: {ds3.nbytes/1024**2:.3f}')


