# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 07:44:47 2024

@author: veenstra
"""

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
