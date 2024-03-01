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
    location = locations[locations['Grootheid.Code'] == 'WATHTE'].loc['DENHDR']
    return location

def test_measurements_available(location):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    data_present = ddlpy.ddlpy._measurements_available(location, start_date=start_date, end_date=end_date)
    assert isinstance(data_present, bool)

def test_measurements(location):
    """measurements for a location """
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
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
    """https://github.com/openearth/ddlpy/issues/27"""
    # input parameters
    start_date  = dt.datetime(2019,11,24)
    end_date = dt.datetime(2019,12,5)
    meas_wathte = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert meas_wathte["t"].is_monotonic_increasing == True
    meas_wathte_clean = ddlpy.measurements(location, start_date=start_date, end_date=end_date, clean_df=True)
    assert meas_wathte_clean["t"].is_monotonic_increasing == True
    meas_wathte_raw = ddlpy.measurements(location, start_date=start_date, end_date=end_date, clean_df=False)
    assert meas_wathte_raw["t"].is_monotonic_increasing == False
    # check wheter indexes are contiguous (due to reset_index)
    assert isinstance(meas_wathte_clean.index, pd.RangeIndex)
    assert isinstance(meas_wathte_raw.index, pd.RangeIndex)

def test_measurements_duplicated(location):
    """
    WALSODN 2010 contains all values three times, ddlpy drops duplicates
    https://github.com/openearth/ddlpy/issues/24
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
    # check wheter indexes are contiguous (due to reset_index)
    assert isinstance(measurements_clean.index, pd.RangeIndex)
    assert isinstance(measurements_raw.index, pd.RangeIndex)

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert 'ddlpy.cli' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
