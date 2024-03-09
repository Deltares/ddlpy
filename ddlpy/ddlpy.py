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
import numpy as np

from .utils import date_series

BASE_URL = "https://waterwebservices.rijkswaterstaat.nl/"
ENDPOINTS_PATH = pathlib.Path(__file__).with_name("endpoints.json")

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
    endpoint = ENDPOINTS["collect_catalogue"]
    msg = "{} with {}".format(endpoint["url"], json.dumps(endpoint["request"]))
    logger.debug("requesting: {}".format(msg))

    resp = requests.post(endpoint["url"], json=endpoint["request"])
    if not resp.ok:
        raise IOError("Failed to request {}: {}".format(msg, resp.text))
    result = resp.json()
    if not result["Succesvol"]:
        logger.exception(str(result))
        raise ValueError(result.get("Foutmelding", "No error returned"))

    df_locations = pd.DataFrame(result["LocatieLijst"])

    df_metadata = pd.json_normalize(result["AquoMetadataLijst"])

    df_metadata_location = pd.DataFrame(result["AquoMetadataLocatieLijst"])

    merged = (
        df_metadata_location.set_index("Locatie_MessageID")
        .join(df_locations.set_index("Locatie_MessageID"), how="inner")
        .reset_index()
    )
    merged = merged.set_index("AquoMetaData_MessageID").join(
        df_metadata.set_index("AquoMetadata_MessageID")
    )
    # set station id as index
    return merged.set_index("Code")


def _get_request_dicts(location):
    aquometadata_dict = {
        "Eenheid": {"Code": location["Eenheid.Code"]},
        "Grootheid": {"Code": location["Grootheid.Code"]},
        "Hoedanigheid": {"Code": location["Hoedanigheid.Code"]},
        "Groepering": {"Code": location["Groepering.Code"]},
    }
    
    locatie_dict = {
        "X": location["X"],
        "Y": location["Y"],
        # assert code is used as index
        # TODO: use  a numpy  compatible json encoder in requests
        "Code": location.get("Code", location.name),
    }
    
    request_dicts = {"AquoMetadata": aquometadata_dict,
                     "Locatie": locatie_dict}
    return request_dicts


def measurements_available(location, start_date, end_date):
    """checks if there are measurements for location, for the period start_date, end_date
    gives None if check was unsuccesfull
    gives True/False if there are / are no measurement available
    """
    endpoint = ENDPOINTS['check_observations_available']

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    
    start_date_str = pytz.UTC.localize(start_date).isoformat(timespec='milliseconds')
    end_date_str = pytz.UTC.localize(end_date).isoformat(timespec='milliseconds')

    request_dicts = _get_request_dicts(location)

    request = {
        "AquoMetadataLijst": [request_dicts["AquoMetadata"]],
        "LocatieLijst": [request_dicts["Locatie"]],
        "Periode": {
            "Begindatumtijd": start_date_str,
            "Einddatumtijd": end_date_str
        }
    }

    try:
        logger.debug('requesting:  {}'.format(request))
        resp = requests.post(endpoint['url'], json=request, timeout=5)
        result = resp.json()
        if not result['Succesvol']:
            logger.debug('Got  invalid response: {}'.format(result))
            raise NoDataException(result.get('Foutmelding', 'No error returned'))
    except NoDataException as e:
        logger.debug('No data availble for {} {}'.format(start_date, end_date))
        raise e

    if result['Succesvol']:
        if result['WaarnemingenAanwezig'] == 'true' :
            return True
        else:
            return False  


def _combine_waarnemingenlijst(result, location):
    assert "WaarnemingenLijst" in result
    
    # assert len(result['WaarnemingenLijst']) == 1
    # flatten the datastructure
    rows = []
    for waarneming in result["WaarnemingenLijst"]:
        for row in waarneming["MetingenLijst"]:
            # metadata is a list of 1 value, flatten it
            new_row = {}
            for key, value in row["WaarnemingMetadata"].items():
                new_key = "WaarnemingMetadata." + key
                new_val = value[0] if len(value) == 1 else value
                new_row[new_key] = new_val

            # add remaining data
            for key, val in row.items():
                if key == "WaarnemingMetadata":
                    continue
                new_row[key] = val

            # add metadata
            for key, val in list(waarneming["AquoMetadata"].items()):
                if isinstance(val, dict) and "Code" in val and "Omschrijving" in val:
                    # some values have a code/omschrijving pair, flatten them
                    new_key = key + ".Code"
                    new_val = val["Code"]
                    new_row[new_key] = new_val

                    new_key = key + ".Omschrijving"
                    new_val = val["Omschrijving"]
                    new_row[new_key] = new_val
                else:
                    new_row[key] = val
            rows.append(new_row)
    # normalize and return
    df = pd.json_normalize(rows)
    
    # add other info
    df["Code"] = location.get("Code", location.name)

    for name in [
        "Coordinatenstelsel",
        "Naam",
        "X",
        "Y",
        "Parameter_Wat_Omschrijving",
    ]:
        df[name] = location[name]

    # set NA value
    if "WaarnemingMetadata.KwaliteitswaardecodeLijst" in df.columns:
        bool_nan = df["WaarnemingMetadata.KwaliteitswaardecodeLijst"] == "99"
        if "Meetwaarde.Waarde_Numeriek" in df.columns:
            df.loc[bool_nan,"Meetwaarde.Waarde_Numeriek"] = np.nan
    
    try:
        df["time"] = pd.to_datetime(df["Tijdstip"])
        df = df.set_index("time")
    except KeyError:
        logger.exception(
            "Cannot add time variable time because variable Tijdstip is not found"
        )

    return df


def _measurements_slice(location, start_date, end_date):
    """get measurements for location, for the period start_date, end_date, use measurements instead"""
    endpoint = ENDPOINTS["collect_observations"]

    start_date_str = pytz.UTC.localize(start_date).isoformat(timespec="milliseconds")
    end_date_str = pytz.UTC.localize(end_date).isoformat(timespec="milliseconds")
    
    request_dicts = _get_request_dicts(location)
    
    request = {
        "AquoPlusWaarnemingMetadata": {
            "AquoMetadata": request_dicts["AquoMetadata"]
            },
        "Locatie": request_dicts["Locatie"],
        "Periode": {"Begindatumtijd": start_date_str, 
                    "Einddatumtijd": end_date_str},
    }

    try:
        logger.debug("requesting:  {}".format(request))
        resp = requests.post(endpoint["url"], json=request)
        result = resp.json()
        if not result["Succesvol"]:
            logger.debug("Got  invalid response: {}".format(result))
            raise NoDataException(result.get("Foutmelding", "No error returned"))
    except NoDataException as e:
        logger.debug("No data availble for {} {}".format(start_date, end_date))
        raise e
    
    df = _combine_waarnemingenlijst(result, location)
    return df


def measurements(location, start_date, end_date, clean_df=True):
    """return measurements for the given location and time window (start_date, end_date)"""
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    
    measurements = []

    # data_present = measurements_available(
    #         location, start_date=start_date, end_date=end_date)
    # if not data_present:
    #     # early return in case of no data
    #     logger.debug("no data found for this station and time extent")
    #     return
    
    for (start_date_i, end_date_i) in tqdm.tqdm(
        date_series(start_date, end_date, freq=dateutil.rrule.MONTHLY)
    ):
        """return measurements for station given by locations record \"location\", from start_date through end_date
        IMPORTANT: measurements made every 10 minutes will not be downoladed if freq= YEAR.
        For instance if many duplicate timesteps are present, it will fail or timeout.
        Therefore, Please DO NOT CHANGE THE FREQUENCY TO YEAR. KEEP IT MONTHLY NO MATTER HOW SLOW THE CODE CAN BE!
        """

        try:
            measurement = _measurements_slice(
                location, start_date=start_date_i, end_date=end_date_i
            )
            measurements.append(measurement)
        except NoDataException:
            continue

    if len(measurements) == 0:
        # early return in case of no data
        logger.debug("no data found for this station and time extent")
        return
    
    measurements = pd.concat(measurements)

    if clean_df:
        len_raw = len(measurements)
        # drop duplicate rows (preserves e.g. different Grootheden/Groeperingen at same timestep)
        measurements = measurements.drop_duplicates()
        
        # remove Tijdstap column, has to be done after drop_duplicates to avoid too much to be dropped
        measurements = measurements.drop("Tijdstip", axis=1)
        
        # sort dataframe on time, ddl returns non-sorted data
        measurements = measurements.sort_index()
        ndropped = len_raw - len(measurements)
        logger.debug(f"{ndropped} duplicated values dropped")

    return measurements


def measurements_latest(location):
    """checks if there are measurements for location, for the period start_date, end_date
    gives None if check was unsuccesfull
    gives True/False if there are / are no measurement available
    """
    endpoint = ENDPOINTS['collect_latest_observations']

    request_dicts = _get_request_dicts(location)
    
    request = {"AquoPlusWaarnemingMetadataLijst":[{"AquoMetadata":request_dicts["AquoMetadata"]}],
               "LocatieLijst":[request_dicts["Locatie"]]
               }

    try:
        logger.debug('requesting:  {}'.format(request))
        resp = requests.post(endpoint['url'], json=request, timeout=5)
        result = resp.json()
        if not result['Succesvol']:
            logger.debug('Got  invalid response: {}'.format(result))
            raise NoDataException(result.get('Foutmelding', 'No error returned'))
    except NoDataException as e:
        logger.debug('No data availble')
        raise e

    if result['Succesvol']:
        df = _combine_waarnemingenlijst(result, location)
        return df


def simplify_dataframe(df: pd.DataFrame):
    """
    drop columns with constant values from the dataframe
    and collect them in a dictionary which is 
    added as attrs of the dataframe
    """
    
    bool_constant = (df == df.iloc[0]).all()
    
    # constant columns are flattened and converted to dict of attrs
    df_attrs = df.loc[:, bool_constant].iloc[0].to_dict()
    
    # varying columns are kept in output dataframe
    df_simple = df.loc[:, ~bool_constant]
    
    # attach as attrs to dataframe
    df_simple.attrs = df_attrs
    
    return df_simple
