#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddlpy` package."""
import datetime as dt
import pandas as pd
import pytest
from click.testing import CliRunner
import ddlpy
from ddlpy import cli


def test_locations():
    locations = ddlpy.locations()
    assert locations.shape[0] > 1


@pytest.fixture
def location():
    """return sample location"""
    locations = ddlpy.locations()
    bool_grootheid = locations['Grootheid.Code'] == 'WATHTE'
    bool_groepering = locations['Groepering.Code'] == 'NVT'
    location = locations[bool_grootheid & bool_groepering].loc['DENHDR']
    return location


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


def test_measurements(location):
    """measurements for a location """
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert measurements.shape[0] > 1


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


def test_measurements_latest(location):
    """measurements for a location """
    latest = ddlpy.measurements_latest(location)
    assert latest.shape[0] > 1


def test_measurements_long(location):
    """measurements for a location """
    start_date = dt.datetime(1951, 11, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert measurements.shape[0] > 1


def test_measurements_sorted(location):
    """https://github.com/deltares/ddlpy/issues/27"""
    # input parameters
    start_date  = dt.datetime(2019,11,24)
    end_date = dt.datetime(2019,12,5)
    meas_wathte = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert meas_wathte.index.is_monotonic_increasing == True
    meas_wathte_clean = ddlpy.measurements(location, start_date=start_date, end_date=end_date, clean_df=True)
    assert meas_wathte_clean.index.is_monotonic_increasing == True
    meas_wathte_raw = ddlpy.measurements(location, start_date=start_date, end_date=end_date, clean_df=False)
    assert meas_wathte_raw.index.is_monotonic_increasing == False
    # check wheter indexes are DatetimeIndex
    assert isinstance(meas_wathte.index, pd.DatetimeIndex)
    assert isinstance(meas_wathte_clean.index, pd.DatetimeIndex)
    assert isinstance(meas_wathte_raw.index, pd.DatetimeIndex)


def test_measurements_duplicated(location):
    """
    WALSODN 2010 contains all values three times, ddlpy drops duplicates
    https://github.com/deltares/ddlpy/issues/24
    if the data is cleaned in ddl, this test will fail and can be removed or adjusted
    """
    locations = ddlpy.locations()
    location = locations[locations['Grootheid.Code'] == 'WATHTE'].loc['WALSODN']
    start_date = dt.datetime(2010, 1, 1)
    end_date = dt.datetime(2010, 1, 1, 0, 20)
    measurements_clean = ddlpy.measurements(location, start_date=start_date, end_date=end_date, clean_df=True)
    measurements_raw = ddlpy.measurements(location, start_date=start_date, end_date=end_date, clean_df=False)
    assert len(measurements_clean) == 3
    assert len(measurements_raw) == 9
    # check wheter indexes are DatetimeIndex
    assert isinstance(measurements_clean.index, pd.DatetimeIndex)
    assert isinstance(measurements_raw.index, pd.DatetimeIndex)


def test_measurements_remove_duplicates_nottoomuch(location):
    """
    to prevent issue https://github.com/deltares/ddlpy/issues/53
    """
    start_date = dt.datetime(2014, 1, 1)
    end_date = dt.datetime(2014, 1, 7)
    measurements_clean = ddlpy.measurements(location, start_date=start_date, end_date=end_date, clean_df=True)
    measurements_raw = ddlpy.measurements(location, start_date=start_date, end_date=end_date, clean_df=False)
    assert len(measurements_clean) == len(measurements_raw)


def test_simplify_dataframe(location):
    start_date = dt.datetime(2019,11,24)
    end_date = dt.datetime(2019,12,5)
    meas_wathte = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert len(meas_wathte.columns) == 53
    meas_simple = ddlpy.simplify_dataframe(meas_wathte)
    assert hasattr(meas_simple, "attrs")
    assert len(meas_simple.attrs) == 51
    assert len(meas_simple.columns) == 2


datetype_list = ["string", "pd.Timestamp", "dt.datetime", "mixed"]
@pytest.mark.parametrize("datetype", datetype_list)
def test_check_convert_dates(datetype):
    start_date_str = "1953-01-01"
    end_date_str = "1953-04-01"
    start_date_pd = pd.Timestamp(start_date_str)
    end_date_pd = pd.Timestamp(start_date_str)
    start_date_dt = dt.datetime(start_date_pd)
    end_date_dt = dt.datetime(end_date_pd)
    if datetype == "string":
        start_date = start_date_str
        end_date = end_date_str
    elif datetype == "pd.Timestamp":
        start_date = start_date_pd
        end_date = end_date_pd
    elif datetype == "dt.datetime":
        start_date = start_date_dt
        end_date = end_date_dt
    elif datetype == "mixed":
        start_date = start_date_str
        end_date = end_date_dt

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


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output
    help_result = runner.invoke(cli.cli, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output

