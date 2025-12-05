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

    locations_command = 'locations --procestype astronomisch --grootheid-code WATHTE --station hoekvanholland'
    locations_result = runner.invoke(cli.cli, locations_command.split())
    assert locations_result.exit_code == 0
    file_locs = "locations.json"
    assert os.path.exists(file_locs)
    
    measurements_command = 'measurements 2023-01-01 2023-01-03'
    measurements_result = runner.invoke(cli.cli, measurements_command.split())
    assert measurements_result.exit_code == 0
    file_meas = "hoekvanholland_astronomisch_OW_cm_WATHTE__NAP_NVT.csv"
    assert os.path.exists(file_meas)
    file_ext = "hoekvanholland_astronomisch_OW_cm_WATHTE_GETETBRKD2_NAP_NVT.csv"
    assert os.path.exists(file_ext)
    
    # TODO: this currently retrieves two files, one for measurement timeseries, one for extremes.
    # TODO: subsetting `--groepering-code ""` (measurement timeseries) results in an empty locations.json, this is because it is being parsed as '""', which is not present in the columns
