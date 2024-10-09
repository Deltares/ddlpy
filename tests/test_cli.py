# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 07:44:47 2024

@author: veenstra
"""

import os
from click.testing import CliRunner
from ddlpy import cli

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output
    help_result = runner.invoke(cli.cli, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output

    locations_command = 'locations --grootheid-code WATHTE --station hoekvanholland'
    locations_result = runner.invoke(cli.cli, locations_command.split())
    assert locations_result.exit_code == 0
    file_locs = "locations.json"
    assert os.path.exists(file_locs)
    
    measurements_command = 'measurements 2023-01-01 2023-01-03'
    measurements_result = runner.invoke(cli.cli, measurements_command.split())
    assert measurements_result.exit_code == 0
    file_meas = "hoekvanholland_OW_cm_WATHTE_GETETBRKD2_NAP_NVT.csv"
    assert os.path.exists(file_meas)
    # TODO: resulting file does not contain normal waterlevels, only extremes
    # subsetting `--groepering-code ""` results in an empty locations.json
    # but this might be because there are no measurements available for this period in the beta-waterwebservices?
    
    # cleanup
    os.remove(file_locs)
    os.remove(file_meas)
