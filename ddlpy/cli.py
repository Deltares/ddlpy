# -*- coding: utf-8 -*-

"""Console script for ddlpy."""
import sys
import io
import logging

import click

import ddlpy


@click.group()
@click.option('-v', '--verbose', count=True)
def cli(verbose,  args=None):
    """Console script for ddlpy."""
    level = logging.INFO
    if verbose >= 1:
        level = logging.DEBUG
    logging.basicConfig(level=level)
    return 0


@cli.command()
@click.argument('output', type=click.File('w'))
@click.option(
    '--quantity',
    help='Quantity (Grootheid) codes',
    multiple=True
)
@click.option(
    '--station',
    help='Station codes',
    multiple=True
)
@click.option(
    '--format',
    default='csv',
    help='output file format',
    type=click.Choice(['csv', 'json'], case_sensitive=True)
)
def locations(output, station, quantity, format):
    """Write locations to output file"""
    locations = ddlpy.locations()

    # we have multiple of these, let's rename them
    stations = station
    quantities = quantity

    selected = locations

    if (stations):
        selected = selected[selected.index.isin(stations)]
    if quantities:
        selected = selected[selected['Grootheid.Code'].isin(quantities)]

    if format == 'csv':
        selected.to_csv(output)
    elif format == 'json':
        selected.to_json(output, orient='records')
    else:
        raise ValueError('Unexpected format {}'.format(format))


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
