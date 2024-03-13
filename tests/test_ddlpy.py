#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddlpy` package."""
import datetime as dt
import pandas as pd
import pytest
import ddlpy


@pytest.fixture
def locations():
    """return all locations"""
    locations = ddlpy.locations()
    return locations


@pytest.fixture
def location(locations):
    """return sample location"""
    bool_grootheid = locations['Grootheid.Code'] == 'WATHTE'
    bool_groepering = locations['Groepering.Code'] == 'NVT'
    location = locations[bool_grootheid & bool_groepering].loc['DENHDR']
    return location


@pytest.fixture
def measurements(location):
    """measurements for a location """
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    return measurements


def test_locations(locations):
    assert locations.shape[0] > 1


def test_measurements(measurements):
    assert measurements.shape[0] > 1


def test_measurements_available(location):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    data_present = ddlpy.measurements_available(location, start_date=start_date, end_date=end_date)
    assert isinstance(data_present, bool)


def test_measurements_amount(location):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 5)
    data_amount_dag = ddlpy.measurements_amount(location, start_date=start_date, end_date=end_date, period="Dag")
    assert data_amount_dag.shape[0] > 50
    assert data_amount_dag["Groeperingsperiode"].str.len().iloc[0] == 10
    data_amount_maand = ddlpy.measurements_amount(location, start_date=start_date, end_date=end_date, period="Maand")
    assert data_amount_maand.shape[0] == 4
    assert data_amount_maand["Groeperingsperiode"].str.len().iloc[0] == 7
    data_amount_jaar = ddlpy.measurements_amount(location, start_date=start_date, end_date=end_date, period="Jaar")
    assert data_amount_jaar.shape[0] == 1
    assert data_amount_jaar["Groeperingsperiode"].str.len().iloc[0] == 4


def test_measurements_latest(location):
    """measurements for a location """
    latest = ddlpy.measurements_latest(location)
    assert latest.shape[0] > 1


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


def test_simplify_dataframe(measurements):
    assert len(measurements.columns) == 53
    meas_simple = ddlpy.simplify_dataframe(measurements)
    assert hasattr(meas_simple, "attrs")
    assert len(meas_simple.attrs) == 50
    assert len(meas_simple.columns) == 3


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

