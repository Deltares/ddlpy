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


#Define a command
# Each command has options which are read from the console.
@cli.command()
@click.argument('output', type=click.File('w'))
@click.option(
    '--quantity',
    '-qa',
    help='Grootheid code',
    multiple=True
)
@click.option(
    '--quality',
    '-ql',
    help= 'Hoedanigheid code',
    multiple = True
)
@click.option(
    '--unit',
    '-u',
    help= 'Eenheid code',
    multiple = True
)
@click.option(
    '--parameter-code',
    '-pc',
    help= 'Parameter code',
    multiple = True
)
@click.option(
    '--compartment-code',
    '-cc',
    help= 'Compartment code',
    multiple = True
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
    quantities = {'Grootheid.Code':list(quantity),
                  'Hoedanigheid.Code':list(quality),
                  'Eenheid.Code':list(unit),
                  'Parameter.Code':list(parameter_code),
                  'Compartiment.Code':list(compartment_code)
                  }

    selected = locations_df.copy()

    if (stations):
        selected = selected[selected.index.isin(stations)]

    for q in quantities.keys():
        if (len(quantities[q])!=0 ):
            selected = selected[selected[q].isin(quantities[q])]

    if format == 'csv':
        selected.to_csv(output)
    elif format == 'json':
        selected.to_json(output, orient='records')
    else:
        raise ValueError('Unexpected format {}'.format(format))

# Another command to get the masurements from locations
@cli.command()
#@click.argument('input', type=click.File('r'))
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
    default= 'locations.csv',
    help='csv containing locations and codes'
)
def measurements(locations, start_date, end_date):
    """
    Obtain measurements from file with locations and codes
    """
    if (locations):
        locations_df = pd.read_csv(locations)
    else:
        raise ValueError('You need to specify a location file')

    # conver strings to dates
    if start_date:
        start_date = dateutil.parser.parse(start_date)
    if end_date:
        end_date = dateutil.parser.parse(end_date)

    for obs in range(locations_df.shape[0]):
        selected = locations_df.loc[obs]
        print(selected)
        #measurements= ddlpy._measurements_slice(selected, start_date=start_date_i, end_date=end_date_i)
        measurements = ddlpy.measurements(selected, start_date=start_date, end_date=end_date)

        if (len(measurements) > 0):
            print('Measurements of %s were obtained'%selected['Code'])
            station = selected['Code']
            cc = selected['Compartiment.Code']
            ec = selected['Eenheid.Code']
            gc = selected['Grootheid.Code']
            hc = selected['Hoedanigheid.Code']
            pc = selected['Parameter.Code']
            measurements.to_csv('%s_%s_%s_%s_%s_%s.csv'%(station,cc,ec,gc,hc,pc))
        else:
            print('No Data of station %s were retrieved from Water Info'%selected['Code'])


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
