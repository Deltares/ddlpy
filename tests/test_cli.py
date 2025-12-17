# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 07:44:47 2024

@author: veenstra
"""

import os
from click.testing import CliRunner
from ddlpy import cli
import importlib
from packaging.version import Version


def test_command_line_interface(tmp_path):
    """Test the CLI."""
    os.chdir(tmp_path)
    
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    click_version = Version(importlib.metadata.version("click"))
    # TODO: require click>=8.2.0 after dropping support for Python 3.8 and 3.9
    if click_version >= Version("8.2.0"):
        assert result.exit_code == 2
    else:
        assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output
    help_result = runner.invoke(cli.cli, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output

    # running ddlpy-measurements without first running ddlpy-locations fails
    measurements_command = 'measurements 2023-01-01 2023-01-03'
    measurements_result = runner.invoke(cli.cli, measurements_command.split())
    assert measurements_result.exit_code == 1
    assert "locations.json file not found" in str(measurements_result.exception)

    # run ddlpy-locations
    locations_command = 'locations --procestype astronomisch --grootheid-code WATHTE --station hoekvanholland --groepering-code ""'
    # replace empty string representation ('""') with empty string ("")
    locations_command_split = locations_command.split()
    locations_command_split = ["" if x == '""' else x for x in locations_command_split]
    locations_result = runner.invoke(cli.cli, locations_command_split)
    assert locations_result.exit_code == 0
    file_locs = "locations.json"
    assert os.path.exists(file_locs)
    
    file_meas = "hoekvanholland_astronomisch_OW_cm_WATHTE__NAP_NVT_NVT.csv"
    
    # running ddlpy-measurements for period without data succeeds but gives no datafile
    measurements_command = 'measurements 2050-01-01 2050-01-03'
    measurements_result = runner.invoke(cli.cli, measurements_command.split())
    assert measurements_result.exit_code == 0
    assert not os.path.exists(file_meas)
    
    # running ddlpy-measurements for a period with data succeeds and gives a datafile
    measurements_command = 'measurements 2023-01-01 2023-01-03'
    measurements_result = runner.invoke(cli.cli, measurements_command.split())
    assert measurements_result.exit_code == 0
    assert os.path.exists(file_meas)