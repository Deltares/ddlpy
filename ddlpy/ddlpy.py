# -*- coding: utf-8 -*-

"""Main module."""
import json
import pathlib
import logging

import requests
import pandas as pd
import pytz
import tqdm
import dateutil

from .utils import date_series

BASE_URL = "https://waterwebservices.rijkswaterstaat.nl/"
ENDPOINTS_PATH = pathlib.Path(__file__).with_name('endpoints.json')

with ENDPOINTS_PATH.open() as f:
    ENDPOINTS = json.load(f)


class NoDataException(ValueError):
    pass

# Web Feature Service
# Web Mapping Service
logger = logging.getLogger(__name__)

def locations():
    """
    get station information from DDL (metadata from Catalogue). All metadata regarding stations.
    The response (result) retrieves more keys

    """
    endpoint = ENDPOINTS['collect_catalogue']
    msg = '{} with {}'.format(endpoint['url'], json.dumps(endpoint['request']))
    logger.debug('requesting: {}'.format(msg))

    resp = requests.post(endpoint['url'], json=endpoint['request'])
    if not resp.ok:
        raise IOError("Failed to request {}: {}".format(msg, resp.text))
    result = resp.json()
    if not result['Succesvol']:
        logger.exception(str(result))
        raise ValueError(result.get('Foutmelding', 'No error returned'))


    df_locations = pd.DataFrame(result['LocatieLijst'])

    df_metadata = pd.json_normalize(
        result['AquoMetadataLijst']
    )

    df_metadata_location = pd.DataFrame(result['AquoMetadataLocatieLijst'])


    merged = df_metadata_location.set_index('Locatie_MessageID').join(
        df_locations.set_index('Locatie_MessageID'),
        how='inner'
    ).reset_index()
    merged = merged.set_index('AquoMetaData_MessageID').join(
        df_metadata.set_index('AquoMetadata_MessageID')
    )
    # set station id as index
    return merged.set_index('Code')


def _measurements_slice(location, start_date, end_date):
    """get measurements for location, for the period start_date, end_date, use measurements instead"""
    endpoint = ENDPOINTS['collect_observations']

    start_date_str = pytz.UTC.localize(start_date).isoformat(timespec='milliseconds')
    end_date_str = pytz.UTC.localize(end_date).isoformat(timespec='milliseconds')


    request = {
        "AquoPlusWaarnemingMetadata": {
            "AquoMetadata": {
                "Eenheid": {
                    "Code": location['Eenheid.Code']
                },
                "Grootheid": {
                    "Code": location['Grootheid.Code']
                },
                "Hoedanigheid": {
                    "Code": location['Hoedanigheid.Code']
                }
            }
        },
        "Locatie": {
            'X': location['X'],
            'Y': location['Y'],
            # assert code is used as index
            # TODO: use  a numpy  compatible json encoder in requests
            'Code': location.get('Code', location.name)
        },
        "Periode": {
            "Begindatumtijd": start_date_str,
            "Einddatumtijd": end_date_str
        }
    }

    try:
        logger.debug('requesting:  {}'.format(request))
        resp = requests.post(endpoint['url'], json=request)
        result = resp.json()
        if not result['Succesvol']:
            logger.debug('Got  invalid response: {}'.format(result))
            raise NoDataException(result.get('Foutmelding', 'No error returned'))
    except NoDataException as e:
        logger.debug('No data availble for {} {}'.format(start_date, end_date))
        raise e

    assert 'WaarnemingenLijst' in result

    #assert len(result['WaarnemingenLijst']) == 1
    # flatten the datastructure
    rows = []
    for waarneming in result['WaarnemingenLijst']:
        for row in waarneming['MetingenLijst']:
        # metadata is a list of 1 value, flatten it
            new_row = {}
            for key, value in row['WaarnemingMetadata'].items():
                new_key = 'WaarnemingMetadata.' + key
                new_val = value[0] if len(value) == 1 else value
                new_row[new_key] = new_val

            # add remaining data
            for key, val in row.items():
                if key == 'WaarnemingMetadata':
                    continue
                new_row[key] = val

            # add metadata
            for key, val in list(waarneming['AquoMetadata'].items()):
                if isinstance(val, dict) and 'Code' in val and 'Omschrijving' in val:
                    # some values have a code/omschrijving pair, flatten them
                    new_key = key + '.code'
                    new_val = val['Code']
                    new_row[new_key] = new_val

                    new_key = key + '.Omschrijving'
                    new_val = val['Omschrijving']
                    new_row[new_key] = new_val
                else:
                    new_row[key] = val

            rows.append(new_row)
    # normalize and return
    df = pd.io.json.json_normalize(rows)
    # set NA value
    if 'Meetwaarde.Waarde_Numeriek' in df.columns:
        df[df['Meetwaarde.Waarde_Numeriek'] == 999999999] = None

    try:
        df['t'] = pd.to_datetime(df['Tijdstip'])
    except KeyError:
        logger.exception('Cannot add time variable t because variable Tijdstip is not found')
    return df



def measurements(location, start_date, end_date):
    """return measurements for the given location and time window (start_date, end_date)"""
    measurements = []

    for (start_date_i, end_date_i) in tqdm.tqdm(date_series(start_date, end_date, freq=dateutil.rrule. MONTHLY)):
        """return measurements for station given by locations record \"location\", from start_date through end_date
         IMPORTANT: measurements made every 10 minutes will not be downoladed if freq= YEAR.
         Please, DO NOT CHANGE THE FREQUENCY TO YEAR. KEEP IT MONTHLY NO MATTER HOW SLOW THE CODE CAN BE!
        """

        try:
            measurement = _measurements_slice(location, start_date=start_date_i, end_date=end_date_i)
            measurements.append(measurement)
        except NoDataException:
            continue


    if ( len(measurements)> 0 ):
        measurements = pd.concat(measurements)
        measurements = measurements.drop_duplicates()
        # add other info
        measurements['locatie_code'] = location.get('Code', location.name)

        for name in ['Coordinatenstelsel', 'Naam', 'X', 'Y', 'Parameter_Wat_Omschrijving']:
           measurements[name]= location[name]


    return measurements
