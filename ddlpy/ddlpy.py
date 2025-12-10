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


class NoDataError(ValueError):
    pass


class UnsuccessfulRequestError(ValueError):
    pass


# Web Feature Service
# Web Mapping Service
logger = logging.getLogger(__name__)


def _send_post_request(url, request, timeout=None):
    logger.debug("Requesting at {} with request: {}".format(url, json.dumps(request)))
    resp = requests.post(url, json=request, timeout=timeout)
    if not resp.ok:
        raise IOError("Request failed: {}".format(resp.text))
    
    result = resp.json()
    if not result['Succesvol']:
        logger.debug('Response result is unsuccessful: {}'.format(result))
        error_message = result.get('Foutmelding', 'No error returned')
        if error_message == "Geen gegevens gevonden!":
            # Foutmelding: "Geen gegevens gevonden!"
            # this is a valid response for periods where there is no data
            # this error is raised here, but catched in ddlpy.ddlpy.measurements() so the process can continue.
            raise NoDataError(error_message)
        else:
            # Foutmelding: "Het max aantal waarnemingen (157681) is overschreven, beperk uw request."
            # or any other possible error message are raised here
            raise UnsuccessfulRequestError(error_message)
    
    # continue if request was successful
    return result


def catalog(catalog_filter=None):
    endpoint = ENDPOINTS["collect_catalogue"]
    
    if catalog_filter is None:
        # use the default request from endpoints.json
        request = endpoint["request"]
    else:
        assert isinstance(catalog_filter, list)
        request = {"CatalogusFilter": {x:True for x in catalog_filter}}
    
    result = _send_post_request(endpoint["url"], request, timeout=None)
    
    return result


def locations(catalog_filter:list = None) -> pd.DataFrame:
    """
    Get station information from DDL (metadata from Catalogue). All metadata regarding stations.

    Parameters
    ----------
    catalog_filter : list, optional
        list of catalogs to pass on to OphalenCatalogus CatalogusFilter, 
        if None the list form endpoints.json is retrieved. The default is None.

    Returns
    -------
    pd.DataFrame
        DataFrame with a combination of available locations and measurements.

    """

    result = catalog(catalog_filter=catalog_filter)
    
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


def _check_convert_dates(start_date, end_date, return_str=True):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    
    # check if timezones are the same
    assert start_date.tz == end_date.tz
    
    # set UTC timezone if tz is None
    if start_date.tz is None:
        start_date = pytz.UTC.localize(start_date)
    if end_date.tz is None:
        end_date = pytz.UTC.localize(end_date)
    
    if start_date > end_date:
        raise ValueError(f"start_date {start_date} is larger than end_date {end_date}")
    
    if return_str:
        start_date_str = start_date.isoformat(timespec='milliseconds')
        end_date_str = end_date.isoformat(timespec='milliseconds')
        return start_date_str, end_date_str
    else:
        return start_date, end_date


def _get_request_dicts(location):
    
    # generate aquometadata dict from location "*.Code" values
    key_list = [x.replace(".Code","") for x in location.index if x.endswith(".Code")]
    aquometadata_dict = {key:{"Code":location[f"{key}.Code"]} for key in key_list}
    
    # generate location dict from relevant values
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


def measurements_available(location:pd.Series, start_date:(str,pd.Timestamp), end_date:(str,pd.Timestamp)) -> bool:
    """
    Checks if there are measurements available for a location in the requested period.
    
    Parameters
    ----------
    location : pd.Series
        Single row of the `ddlpy.locations()` DataFrame.
    start_date : (str,pd.Timestamp)
        The start date of the requested period.
    end_date : (str,pd.Timestamp)
        The end date of the requested period.

    Returns
    -------
    bool
        Whether there are measurements available or not.

    """
    endpoint = ENDPOINTS['check_observations_available']

    start_date_str, end_date_str = _check_convert_dates(start_date, end_date, return_str=True)

    request_dicts = _get_request_dicts(location)

    request = {
        "AquoMetadataLijst": [request_dicts["AquoMetadata"]],
        "LocatieLijst": [request_dicts["Locatie"]],
        "Periode": {
            "Begindatumtijd": start_date_str,
            "Einddatumtijd": end_date_str
        }
    }

    result = _send_post_request(endpoint["url"], request, timeout=5)
    
    # continue if request was successful
    logger.debug('Got response: {}'.format(result))
    if result['WaarnemingenAanwezig'] == 'true' :
        return True
    else:
        return False  


def measurements_amount(location:pd.Series, start_date:(str,pd.Timestamp), end_date:(str,pd.Timestamp), 
                        period:str = "Jaar") -> pd.DataFrame:
    """
    Retrieves the amount of measurements available for a location for the requested period.

    Parameters
    ----------
    location : pd.Series
        Single row of the `ddlpy.locations()` DataFrame.
    start_date : (str,pd.Timestamp)
        The start date of the requested period.
    end_date : (str,pd.Timestamp)
        The end date of the requested period.
    period : str, optional
        "Jaar", "Maand" or "Dag". The default is "Jaar".

    Returns
    -------
    df_amount : pd.DataFrame
        A DataFrame with the number of mesurements (AantalMetingen) per period (Groeperingsperiode).

    """
    # TODO: there are probably more Groeperingsperiodes accepted by ddl, but not supported by ddlpy yet
    accepted_period = ["Jaar","Maand","Dag"]
    if period not in accepted_period:
        raise ValueError(f"period should be one of {accepted_period}, not '{period}'")
    
    endpoint = ENDPOINTS['collect_number_of_observations']
    
    start_date_str, end_date_str = _check_convert_dates(start_date, end_date, return_str=True)

    request_dicts = _get_request_dicts(location)

    request = {
        "AquoMetadataLijst": [request_dicts["AquoMetadata"]],
        "LocatieLijst": [request_dicts["Locatie"]],
        "Groeperingsperiode": period,
        "Periode": {
            "Begindatumtijd": start_date_str,
            "Einddatumtijd": end_date_str
        }
    }

    result = _send_post_request(endpoint["url"], request, timeout=None)

    # continue if request was successful
    df_list = []
    for one in result['AantalWaarnemingenPerPeriodeLijst']:
        df = pd.json_normalize(one['AantalMetingenPerPeriodeLijst'])
        
        # combine columns to a period string
        df["Groeperingsperiode"] = df["Groeperingsperiode.Jaarnummer"].apply(lambda x: f"{x:04d}")
        if period in ["Maand", "Dag"]:
            df["Groeperingsperiode"] = (df["Groeperingsperiode"] + "-" + 
                                        df["Groeperingsperiode.Maandnummer"].apply(lambda x: f"{x:02d}"))
        if period in ["Dag"]:
            df["Groeperingsperiode"] = (df["Groeperingsperiode"] + "-" + 
                                        df["Groeperingsperiode.Dag"].apply(lambda x: f"{x:02d}"))
        
        # select columns from dataframe and append to list
        df = df.set_index("Groeperingsperiode")
        df = df[["AantalMetingen"]]
        df_list.append(df)
        
    # concatenate and sum duplicated index
    df_amount = pd.concat(df_list).sort_index()
    df_amount = df_amount.groupby(df_amount.index).sum()
    return df_amount


def _combine_waarnemingenlijst(result, location):
    assert "WaarnemingenLijst" in result
    
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
    ]:
        df[name] = location[name]

    # set NA value
    if "WaarnemingMetadata.KwaliteitswaardecodeLijst" in df.columns:
        bool_nan = df["WaarnemingMetadata.KwaliteitswaardecodeLijst"] == "99"
        if "Meetwaarde.Waarde_Numeriek" in df.columns:
            df.loc[bool_nan,"Meetwaarde.Waarde_Numeriek"] = np.nan
    
    try:
        df["time"] = pd.to_datetime(df["Tijdstip"], format="ISO8601")
        df = df.set_index("time")
    except KeyError:
        logger.exception(
            "Cannot add time variable time because variable Tijdstip is not found"
        )

    return df


def _measurements_slice(location, start_date, end_date):
    """get measurements for location, for the period start_date, end_date, use measurements instead"""
    endpoint = ENDPOINTS["collect_observations"]

    start_date_str, end_date_str = _check_convert_dates(start_date, end_date, return_str=True)

    request_dicts = _get_request_dicts(location)
    
    request = {
        "AquoPlusWaarnemingMetadata": {
            "AquoMetadata": request_dicts["AquoMetadata"]
            },
        "Locatie": request_dicts["Locatie"],
        "Periode": {"Begindatumtijd": start_date_str, 
                    "Einddatumtijd": end_date_str},
    }

    result = _send_post_request(endpoint["url"], request, timeout=None)

    df = _combine_waarnemingenlijst(result, location)
    return df


def _clean_dataframe(measurements):
    len_raw = len(measurements)
    # drop duplicate rows (preserves e.g. different Grootheden/Groeperingen at same timestep)
    measurements = measurements.drop_duplicates()
    
    # remove Tijdstip column, has to be done after drop_duplicates to avoid too much to be dropped
    measurements = measurements.drop("Tijdstip", axis=1)
    
    # sort dataframe on time, ddl returns non-sorted data
    measurements = measurements.sort_index()
    ndropped = len_raw - len(measurements)
    logger.debug(f"{ndropped} duplicated values dropped")
    return measurements


def measurements(location:pd.Series, start_date:(str,pd.Timestamp), end_date:(str,pd.Timestamp), 
                 freq:int = dateutil.rrule.MONTHLY, clean_df:bool = True):
    """
    Returns measurements for the given location and requested period.

    Parameters
    ----------
    location : pd.Series
        Single row of the `ddlpy.locations()` DataFrame.
    start_date : str, pd.Timestamp
        Start of the retrieval period.
    end_date : str, pd.Timestamp
        End of the retrieval period.
    freq : int, dateutil.rrule.MONTHLY, dateutil.rrule.YEARLY, etc., optional
        The frequency in which to divide the requested period (e.g. yearly or monthly).
        Can also be None, in which case the entire dataset will be retrieved at once.
        Please note that 10-minute measurements can often not be downloaded in yearly (or larger) chunks 
        since the DDL limits the responses to 157681 values and several stations have duplicated timesteps.
        In that case the query will fail with an error or timeout or just return an empty result (as if there was no data).
        In that case, the user should fallback to monthly chunks.
        This is significantly slower but it is also much more robust. The default is dateutil.rrule.MONTHLY.
    clean_df : bool, optional
        Whether to sort the dataframe and remove duplicate rows. The default is True.
    
    Returns
    -------
    measurements : pd.DataFrame
        DataFrame with measurements.
    """
    
    if isinstance(location, pd.DataFrame):
        raise TypeError("The provided location is a pandas.DataFrame, but should be a pandas.Series, "
                        "supply only one location/row instead, for instance by doing 'location.iloc[0]'")
    
    start_date, end_date = _check_convert_dates(start_date, end_date, return_str=False)
    
    measurements = []

    # data_present = measurements_available(
    #         location, start_date=start_date, end_date=end_date)
    # if not data_present:
    #     # early return in case of no data
    #     logger.debug("no data found for this station and time extent")
    #     return
    
    if freq is None:
        date_series_iterator = tqdm.tqdm([(start_date, end_date)])
    else:
        date_series_iterator = tqdm.tqdm(
            date_series(start_date, end_date, freq=freq)
        )
    
    for (start_date_i, end_date_i) in date_series_iterator:
        try:
            measurement = _measurements_slice(
                location, start_date=start_date_i, end_date=end_date_i
            )
            measurements.append(measurement)
        except NoDataError:
            continue

    if len(measurements) == 0:
        # return empty dataframe in case of no data
        logger.debug("no data found for this station and time extent")
        return pd.DataFrame()
    
    measurements = pd.concat(measurements)

    if clean_df:
        measurements = _clean_dataframe(measurements)
    
    return measurements


def measurements_latest(location:pd.Series) -> pd.DataFrame:
    """
    Returns the latest available measurement for the given location.

    Parameters
    ----------
    location : pd.Series
        Single row of the `ddlpy.locations()` DataFrame.

    Returns
    -------
    df : pd.DataFrame
        DataFrame with measurements.

    """
    endpoint = ENDPOINTS['collect_latest_observations']

    request_dicts = _get_request_dicts(location)
    
    request = {"AquoPlusWaarnemingMetadataLijst":[{"AquoMetadata":request_dicts["AquoMetadata"]}],
               "LocatieLijst":[request_dicts["Locatie"]]
               }

    result = _send_post_request(endpoint["url"], request, timeout=5)
    
    # continue if request was successful
    df = _combine_waarnemingenlijst(result, location)
    return df
