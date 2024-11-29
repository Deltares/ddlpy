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

    locations_command = 'locations --procestype astronomisch --grootheid-code WATHTE --station hoekvanholland'
    locations_result = runner.invoke(cli.cli, locations_command.split())
    assert locations_result.exit_code == 0
    file_locs = "locations.json"
    assert os.path.exists(file_locs)
    
    measurements_command = 'measurements 2023-01-01 2023-01-03'
    measurements_result = runner.invoke(cli.cli, measurements_command.split())
    assert measurements_result.exit_code == 0
    file_meas = "hoekvanholland_astronomisch_OW_cm_WATHTE_GETETBRKD2_NAP_NVT.csv"
    assert os.path.exists(file_meas)
    # TODO: resulting file does not contain normal waterlevels, only extremes. Probably fixed when database is being filled
    # TODO: maybe assert for multiple files being downlaoded, or do more subsetting
    # TODO: subsetting `--groepering-code ""` results in an empty locations.json, this is because it is being parsed as '""', which is not present in the columns
    
    # cleanup
    os.remove(file_locs)
    os.remove(file_meas)
