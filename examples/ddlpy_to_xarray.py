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

# to_xarray
ds1 = measurements.to_xarray()


drop_if_constant = ["WaarnemingMetadata.OpdrachtgevendeInstantieLijst",
                    "WaarnemingMetadata.BemonsteringshoogteLijst",
                    "WaarnemingMetadata.ReferentievlakLijst",
                    "AquoMetadata_MessageID", 
                    "BioTaxonType", #TODO: should also have separate Code/Omschrijving
                    "BemonsteringsSoort.Code", 
                    "Compartiment.Code", "Eenheid.Code", "Grootheid.Code", "Hoedanigheid.Code",
                    ]
ds3 = ddlpy.dataframe_to_xarray(measurements, drop_if_constant)


ds3.to_netcdf("file_nc.nc")
ds_file = xr.open_dataset("file_nc.nc")

print(f'full [MB]: {ds1.nbytes/1024**2:.3f}')
print(f'filt [MB]: {ds3.nbytes/1024**2:.3f}')
print(f'file [MB]: {ds_file.nbytes/1024**2:.3f}')


assert len(ds3["MeetApparaat.Code"]) > 0

for varname in drop_if_constant:
    assert varname not in ds3.data_vars
    assert varname in ds3.attrs.keys()

data_vars_list = ['WaarnemingMetadata.StatuswaardeLijst',
 'WaarnemingMetadata.KwaliteitswaardecodeLijst',
 'MeetApparaat.Code',
 'WaardeBepalingsmethode.Code',
 'Meetwaarde.Waarde_Numeriek']
for varname in data_vars_list:
    assert varname in ds3.data_vars

assert "X" in ds3.attrs.keys()
