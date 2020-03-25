# -*- coding: utf-8 -*-

"""Console script for ddlpy."""
import sys
import io
import logging

import click
import pandas as pd
import dateutil
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


# Define a command
# Each command has options which are read from the console.
@cli.command()
@click.argument('output', type=click.STRING )
@click.option(
    '--quantity',
    help='Grootheid code',
    multiple=True
)
@click.option(
    '--quality',
    help='Hoedanigheid code',
    multiple=True
)
@click.option(
    '--unit',
    help='Eenheid code',
    multiple=True
)
@click.option(
    '--parameter-code',
    help='Parameter code',
    multiple=True
)
@click.option(
    '--compartment-code',
    help='Compartment code',
    multiple=True
)
@click.option(
    '--station',
    help='Station codes',
    multiple=True
)
@click.option(
    '--format',
    default='json',
    help='output file format. Must be json',
    type=click.Choice(['json'], case_sensitive=True)
)
def locations(output,
              station,
              quantity,
              quality,
              unit,
              parameter_code,
              compartment_code,
              format):
    """
    Write locations metadata to output file, given input codes.

    """
    locations_df = ddlpy.locations()

    stations = station
    quantities = {'Grootheid.Code': list(quantity),
                  'Hoedanigheid.Code': list(quality),
                  'Eenheid.Code': list(unit),
                  'Parameter.Code': list(parameter_code),
                  'Compartiment.Code': list(compartment_code)
                  }

    selected = locations_df.copy()

    if (stations):
        selected = selected[selected.index.isin(stations)]

    for q in quantities.keys():
        if (len(quantities[q]) != 0):
            selected = selected[selected[q].isin(quantities[q])]

    selected.reset_index(inplace= True)

    if format == 'json':
        output= output.split('.')[0] # make sure that extension is always json
        selected.to_json(output+'.json', orient='records')
    else:
        raise ValueError('Unexpected format {}'.format(format))

# Another command to get the measurements from locations
@cli.command()
@click.option(
    '--start-date',
    help='Start date of the measurements'
)
@click.option(
    '--end-date',
    help='End date of the measurements'
)
@click.option(
    '--locations',
    default='locations.json',
    help='file in json or parquet format containing locations and codes'
)
def measurements(locations, start_date, end_date):
    """
    Obtain measurements from file with locations and codes
    """
    try:
        locations_df = pd.read_json(locations, orient='records')
    except:
        raise ValueError('location file not existing. Create one or specify its name.')

    # conver strings to dates
    if start_date:
        start_date = dateutil.parser.parse(start_date)
    if end_date:
        end_date = dateutil.parser.parse(end_date)

    for obs in range(locations_df.shape[0]): #goes through rows in table
        selected = locations_df.loc[obs]

        measurements = ddlpy.measurements(
            selected, start_date=start_date, end_date=end_date)

        if (len(measurements) > 0):
            print('Measurements of %s were obtained' % selected['Code'])
            station = selected['Code']
            cc = selected['Compartiment.Code']
            ec = selected['Eenheid.Code']
            gc = selected['Grootheid.Code']
            hc = selected['Hoedanigheid.Code']
            pc = selected['Parameter.Code']

            measurements.to_csv('%s_%s_%s_%s_%s_%s.csv' %
                                (station, cc, ec, gc, hc, pc))
        else:
            print('No Data of station %s were retrieved from Water Info' %
                  selected['Code'])


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
