#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddlpy` package."""
import datetime

import pytest

from click.testing import CliRunner

from ddlpy import ddlpy
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


def test_measurements(location):
    """measurements for a location """
    start_date = datetime.datetime(1953, 1, 1)
    end_date = datetime.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert measurements.shape[0] > 1

def test_measurements_long(location):
    """measurements for a location """
    start_date = datetime.datetime(1951, 11, 1)
    end_date = datetime.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(location, start_date=start_date, end_date=end_date)
    assert measurements.shape[0] > 1

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert 'ddlpy.cli' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
