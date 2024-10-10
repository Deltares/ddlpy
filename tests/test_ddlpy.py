#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddlpy` package."""
import datetime as dt
import pandas as pd
import pytest
import ddlpy
import dateutil
import numpy as np


@pytest.fixture(scope="session")
def locations():
    """return all locations"""
    locations = ddlpy.locations()
    return locations


@pytest.fixture(scope="session")
def location(locations):
    """return sample location"""
    bool_grootheid = locations['Grootheid.Code'] == 'WATHTE'
    bool_procestype = locations['ProcesType'] == 'meting'
    bool_groepering = locations['Groepering.Code'] == ''
    location = locations[bool_grootheid & bool_procestype & bool_groepering].loc['denhelder.marsdiep']
    return location


@pytest.fixture(scope="session")
def measurements(location):
    """measurements for a location """
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    return measurements


def test_locations(locations):
    # the number of columns depend on the catalog filter in endpoints.json
    assert locations.shape[1] == 20
    # the number of rows is the number of stations, so will change over time
    assert locations.shape[0] > 1
    
    # check presence of columns
    assert "Coordinatenstelsel" in locations.columns
    assert "Naam" in locations.columns
    assert "Lon" in locations.columns
    assert "Lat" in locations.columns
    assert "Parameter_Wat_Omschrijving" in locations.columns


def test_locations_extended():
    catalog_filter = ['Compartimenten','Eenheden','Grootheden',
                      'Hoedanigheden','Groeperingen','MeetApparaten',
                      'Typeringen','WaardeBepalingsmethoden','Parameters']
    locations_extended = ddlpy.locations(catalog_filter=catalog_filter)
    # the number of columns depend on the provided catalog_filter
    assert locations_extended.shape[1] == 25
    # the number of rows is the number of stations, so will change over time
    assert locations_extended.shape[0] > 1


def test_measurements(measurements):
    assert measurements.shape[0] > 1
    
    # check presence of columns
    assert "Coordinatenstelsel" in measurements.columns
    assert "Naam" in measurements.columns
    assert "Lon" in measurements.columns
    assert "Lat" in measurements.columns
    assert "Parameter_Wat_Omschrijving" in measurements.columns
    assert "Code" in measurements.columns


def test_measurements_freq_yearly(location, measurements):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements_yearly = ddlpy.measurements(location, start_date=start_date, end_date=end_date, freq=dateutil.rrule.YEARLY)
    assert measurements.shape == measurements_yearly.shape


def test_measurements_freq_none(location, measurements):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements_monthly = ddlpy.measurements(location, start_date=start_date, end_date=end_date, freq=None)
    assert measurements.shape == measurements_monthly.shape


def test_measurements_available(location):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    data_present = ddlpy.measurements_available(location, start_date=start_date, end_date=end_date)
    assert isinstance(data_present, bool)


def test_measurements_amount(location):
    # TODO: revert expected values when database is extended
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 5)
    data_amount_dag = ddlpy.measurements_amount(location, start_date=start_date, end_date=end_date, period="Dag")
    assert data_amount_dag.shape[0] > 10
    assert data_amount_dag.index.str.len()[0] == 10
    data_amount_maand = ddlpy.measurements_amount(location, start_date=start_date, end_date=end_date, period="Maand")
    assert data_amount_maand.shape[0] == 2
    assert data_amount_maand.index.str.len()[0] == 7
    data_amount_jaar = ddlpy.measurements_amount(location, start_date=start_date, end_date=end_date, period="Jaar")
    assert data_amount_jaar.shape[0] == 1
    assert data_amount_jaar.index.str.len()[0] == 4


def test_measurements_amount_multipleblocks(location):
    # in 1993 the WaardeBepalingsmethode changes from
    # other:F001 (Rekenkundig gemiddelde waarde over vorige 10 minuten) to 
    # other:F007 (Rekenkundig gemiddelde waarde over vorige 5 en volgende 5 minuten)
    date_min = "1990-01-01"
    date_max = "1995-01-01"
    # if we pass one row to the measurements function you can get all the measurements
    df_amount = ddlpy.measurements_amount(location, date_min, date_max)
    
    index_expected = np.array(['1990', '1991', '1992', '1993', '1994', '1995'])
    values_expected = np.array([52554, 52560, 52704, 52560, 52560,     7])
    assert (df_amount.index == index_expected).all()
    assert (df_amount["AantalMetingen"].values == values_expected).all()


def test_measurements_latest(location):
    """measurements for a location """
    latest = ddlpy.measurements_latest(location)
    assert latest.shape[0] == 1


def test_measurements_empty(location):
    """measurements for a location """
    start_date = dt.datetime(2153, 1, 1)
    end_date = dt.datetime(2153, 1, 2)
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert measurements.empty


def test_measurements_typerror(locations):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    with pytest.raises(TypeError):
        _ = ddlpy.measurements(locations, start_date=start_date, end_date=end_date)


def test_measurements_noindex(location):
    # pandas dataframe with Code as column instead of index
    locations_noindex = pd.DataFrame(location).T
    locations_noindex.index.name = "Code"
    locations_noindex = locations_noindex.reset_index(drop=False)
    
    # normal subsetting and retrieving
    location_sel = locations_noindex.iloc[0]
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(location_sel, start_date=start_date, end_date=end_date)
    assert measurements.shape[0] > 1


def test_measurements_long(location):
    """measurements for a location """
    start_date = dt.datetime(1951, 11, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert measurements.shape[0] > 1


def test_measurements_sorted(measurements):
    """https://github.com/deltares/ddlpy/issues/27"""
    
    # sort dataframe on values so it will not be sorted on time
    meas_wrongorder = measurements.sort_values("Meetwaarde.Waarde_Numeriek")
    assert meas_wrongorder.index.is_monotonic_increasing == False
    meas_clean = ddlpy.ddlpy._clean_dataframe(meas_wrongorder)
    assert meas_clean.index.is_monotonic_increasing == True
    # assert meas_clean.index.duplicated().sum() == 0
    
    # check wheter indexes are DatetimeIndex
    assert isinstance(meas_wrongorder.index, pd.DatetimeIndex)
    assert isinstance(meas_clean.index, pd.DatetimeIndex)


def test_measurements_duplicated(measurements):
    """
    WALSODN 2010 contains all values three times, ddlpy drops duplicates
    https://github.com/deltares/ddlpy/issues/24
    if the data is cleaned in ddl, this test will fail and can be removed or adjusted
    
    length assertion of meas_clean is important, to prevent issue 
    https://github.com/deltares/ddlpy/issues/53
    """
    
    # deliberately duplicate values in a measurements dataframe
    meas_duplicated = pd.concat([measurements, measurements, measurements], axis=0)
    meas_clean = ddlpy.ddlpy._clean_dataframe(meas_duplicated)
    assert len(meas_duplicated) == 3024
    assert len(meas_clean) == 392
    
    # check wheter indexes are DatetimeIndex
    assert isinstance(meas_duplicated.index, pd.DatetimeIndex)
    assert isinstance(meas_clean.index, pd.DatetimeIndex)


def test_measurements_timezone_behaviour(location):
    start_date = "2015-01-01 00:00:00 +01:00"
    end_date = "2015-01-03 00:00:00 +01:00"
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert str(measurements.index[0].tz) == 'UTC+01:00'
    assert measurements.index[0] == pd.Timestamp(start_date)
    assert measurements.index[-1] == pd.Timestamp(end_date)
    
    data_amount_dag = ddlpy.measurements_amount(location, start_date=start_date, end_date=end_date, period="Dag")
    # when retrieving with tzone +01:00 we expect 1 value on 2015-01-03
    assert np.allclose(data_amount_dag["AantalMetingen"].values, [144,144,1])
    
    
    start_date = "2015-01-01"
    end_date = "2015-01-03"
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert str(measurements.index[0].tz) == 'UTC+01:00'
    assert measurements.index[0] == pd.Timestamp(start_date).tz_localize("UTC").tz_convert('UTC+01:00')
    assert measurements.index[-1] == pd.Timestamp(end_date).tz_localize("UTC").tz_convert('UTC+01:00')
    
    data_amount_dag = ddlpy.measurements_amount(location, start_date=start_date, end_date=end_date, period="Dag")
    # when retrieving with tzone +00:00 we expect 7 values on 2015-01-03
    assert np.allclose(data_amount_dag["AantalMetingen"].values, [138,144,7])


def test_nodataerror(location):
    """
    Test whether a request that returns no data is indeed properly catched
    This is important since it is derived from the returned error message "Geen gegevens gevonden!"
    In case this error message changes in the future, 
    this test will fail and the ddlpy code needs to be updated accordingly
    """
    start_date = dt.datetime(2180, 1, 1)
    end_date = dt.datetime(2180, 4, 1)
    with pytest.raises(ddlpy.ddlpy.NoDataError):
        # ddlpy.measurements() catches NoDataError, so we have to test it with _measurements_slice
        _ = ddlpy.ddlpy._measurements_slice(location, start_date=start_date, end_date=end_date)
    with pytest.raises(ddlpy.ddlpy.NoDataError):
        _ = ddlpy.ddlpy.measurements_amount(location, start_date=start_date, end_date=end_date)


def test_toolargerequest(locations):
    """
    deliberately send a request that is too large to get the error message
    Foutmelding: 'Het maximaal aantal waarnemingen (160000) is overschreven. Beperk uw request.'
    """
    # TODO: we commented this testcase since the old WaterWebservices was very slow in checking this.
    # TODO: when the denhelder dataset is completely filled we can also simulate it with that station
    bool_grootheid = locations['Grootheid.Code'] == 'WATHTE'
    bool_procestype = locations['ProcesType'] == 'meting'
    bool_groepering = locations['Groepering.Code'] == ''
    location = locations[bool_grootheid & bool_procestype & bool_groepering].loc['ameland.nes'].iloc[0]
    
    start_date = dt.datetime(2015, 1, 1)
    end_date = dt.datetime(2020, 1, 1)
    with pytest.raises(IOError) as e:
        #this is the same as ddlpy.measurements(location, start_date=start_date, end_date=end_date, freq=None)
        _ = ddlpy.ddlpy._measurements_slice(location, start_date=start_date, end_date=end_date)
    assert "Het maximaal aantal waarnemingen (160000) is overschreden." in str(e.value)


datetype_list = ["string", "pd.Timestamp", "dt.datetime", "mixed"]
@pytest.mark.parametrize("datetype", datetype_list)
def test_check_convert_dates(datetype):
    if datetype == "string":
        start_date = "1953-01-01"
        end_date = "1953-04-01"
    elif datetype == "pd.Timestamp":
        start_date = pd.Timestamp("1953-01-01")
        end_date = pd.Timestamp("1953-04-01")
    elif datetype == "dt.datetime":
        start_date = dt.datetime(1953,1,1)
        end_date = dt.datetime(1953,4,1)
    elif datetype == "mixed":
        start_date = "1953-01-01"
        end_date = dt.datetime(1953,4,1)

    # assert output
    start_date_out, end_date_out = ddlpy.ddlpy._check_convert_dates(start_date, end_date)
    assert start_date_out=='1953-01-01T00:00:00.000+00:00'
    assert end_date_out=='1953-04-01T00:00:00.000+00:00'


def test_check_convert_wrongorder():
    start_date = "1953-01-01"
    end_date = "1953-04-01"
    
    # assert output
    with pytest.raises(ValueError):
        start_date_out, end_date_out = ddlpy.ddlpy._check_convert_dates(end_date, start_date)


def test_simplify_dataframe(measurements):
    assert len(measurements.columns) == 48
    meas_simple = ddlpy.simplify_dataframe(measurements)
    assert hasattr(meas_simple, "attrs")
    assert len(meas_simple.attrs) == 46
    assert len(meas_simple.columns) == 2


def test_dataframe_to_xarray(measurements):
    drop_if_constant = ["WaarnemingMetadata.OpdrachtgevendeInstantie",
                        "WaarnemingMetadata.Bemonsteringshoogte",
                        "WaarnemingMetadata.Referentievlak",
                        "BemonsteringsSoort.Code", 
                        "Compartiment.Code", "Eenheid.Code", "Grootheid.Code", "Hoedanigheid.Code",
                        ]
    ds_clean = ddlpy.dataframe_to_xarray(measurements, drop_if_constant)
    
    # check if constant value that was not in drop_if_constant list is indeed not dropped
    assert "MeetApparaat.Code" in ds_clean.data_vars
    assert len(ds_clean["MeetApparaat.Code"]) > 0
    
    # TODO: temporary commenting OpdrachtgevendeInstantie checks, since this was not constant before
    # and thus not dropped. With this very limited dataset it is constant, so it is dropped.
    # could be also with complete dataset, but in that case pick another non-constant variable 
    # to test that only constant variables are dropped.
    for varname in drop_if_constant:
        # if varname == "WaarnemingMetadata.OpdrachtgevendeInstantie":
        #     continue
        assert varname not in ds_clean.data_vars
        assert varname in ds_clean.attrs.keys()
    # assert "WaarnemingMetadata.OpdrachtgevendeInstantie" in ds_clean.data_vars
    # assert "WaarnemingMetadata.OpdrachtgevendeInstantie" not in ds_clean.attrs.keys()
    
    data_vars_list = ['WaarnemingMetadata.Statuswaarde',
     'WaarnemingMetadata.Kwaliteitswaardecode',
     'MeetApparaat.Code',
     'WaardeBepalingsMethode.Code',
     'Meetwaarde.Waarde_Numeriek']
    for varname in data_vars_list:
        assert varname in ds_clean.data_vars
    
    assert "Lon" in ds_clean.attrs.keys()
    
    # check if times and timezone are correct
    refdate_utc = measurements.tz_convert(None).index[0]
    ds_firsttime = ds_clean.time.to_pandas().iloc[0]
    assert refdate_utc == ds_firsttime
    assert ds_firsttime.tz is None
