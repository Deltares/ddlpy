# -*- coding: utf-8 -*-

"""
Console script for ddlpy.
    - ``ddlpy --help``
    - ``ddlpy locations --help``
    - ``ddlpy measurements --help``
"""
import sys
import logging
import click
import pandas as pd
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
@click.option(
    '--output', 
    help='the locations json filename that will be created',
    default='locations.json'
    )
@click.option(
    '--station',
    help='Station codes, e.g. HOEKVHLD',
    multiple=True
)
@click.option(
    '--grootheid-code',
    help='Grootheid code, e.g. WATHTE',
    multiple=True
)
@click.option(
    '--groepering-code',
    help='Groepering code, e.g. NVT',
    multiple=True
)
@click.option(
    '--hoedanigheid-code',
    help='Hoedanigheid code, e.g. NAP',
    multiple=True
)
@click.option(
    '--eenheid-code',
    help='Eenheid code, e.g. cm',
    multiple=True
)
@click.option(
    '--parameter-code',
    help='Parameter code',
    multiple=True
)
@click.option(
    '--compartment-code',
    help='Compartment code, e.g. OW',
    multiple=True
)
def locations(output,
              station,
              grootheid_code,
              groepering_code,
              hoedanigheid_code,
              eenheid_code,
              parameter_code,
              compartment_code):
    """
    Subset locations dataframe based on input codes and write locations.json.

    """
    locations_df = ddlpy.locations()

    stations = station
    quantities = {'Grootheid.Code': list(grootheid_code),
                  'Groepering.Code': list(groepering_code),
                  'Hoedanigheid.Code': list(hoedanigheid_code),
                  'Eenheid.Code': list(eenheid_code),
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

    output= output.split('.')[0] # make sure that extension is always json
    selected.to_json(output+'.json', orient='records')

# Another command to get the measurements from locations
@cli.command()
@click.argument(
    'start-date',
)
@click.argument(
    'end-date',
)
@click.option(
    '--locations',
    default='locations.json',
    help='file in json or parquet format containing locations and codes'
)
def measurements(locations, start_date, end_date):
    """
    Obtain measurements from file with locations and codes. 
    The arguments start_date and end_date should be formatted 
    like "YYYY-MM-DD" or something else that `pandas.Timestamp` understands.
    """
    try:
        locations_df = pd.read_json(locations, orient='records')
    except:
        raise ValueError('locations.json file not found. First run "ddlpy locations"')
        
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
            grc = selected['Groepering.Code']
            hc = selected['Hoedanigheid.Code']
            pc = selected['Parameter.Code']

            measurements.to_csv('%s_%s_%s_%s_%s_%s_%s.csv' %
                                (station, cc, ec, gc, grc, hc, pc))
        else:
            print('No Data of station %s were retrieved from Water Info' %
                  selected['Code'])


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
