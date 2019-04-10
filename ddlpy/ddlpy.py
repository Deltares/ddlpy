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
# Locaties
# LocatiesMetLaatsteWaarneming

# Web Mapping Service

logger = logging.getLogger(__name__)

def locations():
    """
    get station information from DDL (metadata uit Catalogus). All metadata regarding stations.
    The response (result) retrieves more keys

    """
    endpoint = ENDPOINTS['collect_catalogue']
    resp = requests.post(endpoint['url'], json=endpoint['request'])
    result = resp.json()
    if not result['Succesvol']:
        logger.exception(str(result))
        raise ValueError(result.get('Foutmelding', 'No error returned'))


    df_locations = pd.DataFrame(result['LocatieLijst'])

    df_metadata = pd.io.json.json_normalize(
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
            'Code': location.name
        },
        "Periode": {
            "Begindatumtijd": start_date_str,
            "Einddatumtijd": end_date_str
        }
    }


    try:
        resp = requests.post(endpoint['url'], json=request)
        result = resp.json()
        if not result['Succesvol']:
            raise NoDataException(result.get('Foutmelding', 'No error returned'))
    except NoDataException as e:
        logger.debug('No data availble for {} {}'.format(start_date, end_date))
        raise e

    assert 'WaarnemingenLijst' in result

    #assert len(result['WaarnemingenLijst']) == 1
    # flatten the datastructure
    rows = []
    for i in range(0, len(result['WaarnemingenLijst']) ):
        for row in result['WaarnemingenLijst'][i]['MetingenLijst']:
        # metadata is a list of 1 value, flatten it
            new_row = {
                'WaarnemingMetadata.' + key: value[0] if len(value) == 1 else value for key, value in row['WaarnemingMetadata'].items()
                }
            # add remaining data
            for key, val in row.items():
                if key == 'WaarnemingMetadata':
                    continue
                new_row[key] = val

            # add metadata
            for key in list(result['WaarnemingenLijst'][i]['AquoMetadata'].keys())[2:]:
                new_row[key+'.code']= result['WaarnemingenLijst'][i]['AquoMetadata'][key]['Code']
                new_row[key+'.Omschrijving']= result['WaarnemingenLijst'][i]['AquoMetadata'][key]['Omschrijving']

            rows.append(new_row)
    # normalize and return
    df = pd.io.json.json_normalize(rows)
    # set NA value
    df[df['Meetwaarde.Waarde_Numeriek'] == 999999999] = None

    try:
        df['t'] = pd.to_datetime(df['Tijdstip'])
    except KeyError:
        logger.exception('Cannot add time variable t because variable Tijdstip is not found')
    return df



def measurements(location, start_date, end_date):
    """return measurements for the given location and time window (start_date, end_date)"""
    measurements = []
    for (start_date_i, end_date_i) in tqdm.tqdm(date_series(start_date, end_date, freq=dateutil.rrule.YEARLY)):
        "return measurements for station given by locations record \"location\", from start_date through end_date"

        try:
            measurement = _measurements_slice(location, start_date=start_date_i, end_date=end_date_i)
            measurements.append(measurement)
        except NoDataException:
            # logging in _measurements_slice
            # up to the next loop
            continue

        #measurements.append(measurement)
    if ( len(measurements)> 0 ):
        measurements = pd.concat(measurements)
        measurements = measurements.drop_duplicates()

    return measurements
