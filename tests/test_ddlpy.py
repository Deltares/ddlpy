#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddlpy` package."""
import datetime as dt
import pandas as pd
import pytest
import ddlpy
import dateutil
import numpy as np
from ddlpy.ddlpy import _send_post_request, NoDataError, get_catalogfile_cache

DTYPES_NONSTRING = {
    "Locatie_MessageID": np.int64,
    "AquoMetadata_MessageID": np.int64,
    "Meetwaarde.Waarde_Numeriek": np.float64,
    "Lon": np.float64,
    "Lat": np.float64,
}


@pytest.fixture(scope="session")
def endpoints():
    """
    Get the endpoints from the api
    """
    endpoints = ddlpy.ddlpy.ENDPOINTS
    return endpoints


@pytest.fixture(scope="session")
def locations():
    """return all locations"""
    locations = ddlpy.locations()
    return locations


@pytest.fixture(scope="session")
def location(locations):
    """return sample location"""
    bool_grootheid = locations["Grootheid.Code"] == "WATHTE"
    bool_groepering = locations["Groepering.Code"] == ""
    bool_procestype = locations["ProcesType"] == "meting"
    location = locations[bool_grootheid & bool_groepering & bool_procestype].loc[
        "denhelder.marsdiep"
    ]
    return location


@pytest.fixture(scope="session")
def measurements(location):
    """measurements for a location"""
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date
    )
    return measurements


def test_send_post_request_errors_wrongapi():
    url = "https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenCatalogus"
    with pytest.raises(IOError) as e:
        _send_post_request(url, request=None)
    assert "404 Not Found" in str(e.value)
    assert "No endpoint POST /ONLINEWAARNEMINGENSERVICES/OphalenCatalogus." in str(
        e.value
    )


def test_send_post_request_errors_ophalencatalogus(endpoints):
    endpoint = endpoints["collect_catalogue"]
    url = endpoint["url"]

    request_empty = {}
    with pytest.raises(IOError) as e:
        _send_post_request(url, request=request_empty)
    assert "400 Bad Request" in str(e.value)
    assert (
        "Het ophalen van de catalogus is mislukt, geen catalogusFilter opgegeven"
        in str(e.value)
    )

    # TODO: this should result in an error by ddapi
    # https://github.com/Rijkswaterstaat/WaterWebservices/issues/18
    request_incorrectkeys = {
        "CatalogusFilter": {
            # 'Eenheden': True, 'Grootheden': True, 'Hoedanigheden': True,
            # 'Groeperingen': True, 'Parameters': True, 'Compartimenten': True,
            "ProcesTypes": True,
            "BioTaxonType": True,
            "ProcesType": True,
            "BioTaxonTypes": True,  # both incorrect in new ddapi
        }
    }
    result = _send_post_request(url, request=request_incorrectkeys)
    assert result["Succesvol"]
    assert result["AquoMetadataLijst"] == []
    assert result["AquoMetadataLocatieLijst"] == []
    assert result["LocatieLijst"] == []
    assert result["StatuswaardeLijst"] == [
        "Ongecontroleerd",
        "Gecontroleerd",
        "Definitief",
    ]


def test_send_post_request_errors_ophalenwaarnemingen(endpoints):
    endpoint = endpoints["collect_observations"]
    url = endpoint["url"]
    request_valid = endpoint["request"]

    request_empty = {}
    with pytest.raises(IOError) as e:
        _send_post_request(url, request=request_empty)
    assert "400 Bad Request" in str(e.value)
    assert "Er moet een periode worden meegegeven als: Periode" in str(e.value)
    assert "Er moet een locatie worden meegegeven als: Locatie" in str(e.value)
    assert (
        "Er moet een AquoPlusObservationMetadata worden meegegeven onder: AquoPlusWaarnemingMetadata"
        in str(e.value)
    )

    request_empty_aquoplus = dict(request_valid)
    request_empty_aquoplus["AquoPlusWaarnemingMetadata"] = {}
    with pytest.raises(IOError) as e:
        _send_post_request(url, request=request_empty_aquoplus)
    assert '400 Bad Request: {"aquoPlusObservationMetadata.aquoMetadata":' in str(
        e.value
    )

    request_invalid_locatie = dict(request_valid)
    request_invalid_locatie["Locatie"] = {"Code": "nonexistent"}
    with pytest.raises(NoDataError) as e:
        _send_post_request(url, request=request_invalid_locatie)
    assert "204 No Content:" in str(e.value)

    request_invalid_periode_order = dict(request_valid)
    request_invalid_periode_order["Periode"] = {
        "Begindatumtijd": "2020-01-01T00:00:00.000+00:00",
        "Einddatumtijd": "2015-01-02T00:00:00.000+00:00",
    }
    with pytest.raises(IOError) as e:
        _send_post_request(url, request=request_invalid_periode_order)
    assert (
        '400 Bad Request: {"period":"De startdatum mag niet na de einddatum zijn onder: Periode."}'
        in str(e.value)
    )

    # TODO: this error is not properly handled by ddapi20
    # https://github.com/Rijkswaterstaat/WaterWebservices/issues/19
    request_invalid_periode_format = dict(request_valid)
    request_invalid_periode_format["Periode"] = {
        "Begindatumtijd": "2015-01-01T00:00:00.000",
        "Einddatumtijd": "2015-01-02T00:00:00.000+00:00",
    }
    with pytest.raises(IOError) as e:
        _send_post_request(url, request=request_invalid_periode_format)
    assert "500 Internal Server Error: Onverwachte fout opgetreden" in str(e.value)

    request_invalid_periode_wrongkeys = dict(request_valid)
    request_invalid_periode_wrongkeys["Periode"] = {
        "Begindatum": "2015-01-01T00:00:00.000+00:00",
        "Einddatum": "2015-01-02T00:00:00.000+00:00",
    }
    with pytest.raises(IOError) as e:
        _send_post_request(url, request=request_invalid_periode_wrongkeys)
    assert '400 Bad Request: {"period.endDateTime":' in str(e.value)

    # TODO: succesful=false is duplicate of resp.ok=False
    # https://github.com/Rijkswaterstaat/WaterWebservices/issues/14
    request_toolarge = dict(request_valid)
    request_toolarge["Periode"] = {
        "Begindatumtijd": "2015-01-01T00:00:00.000+00:00",
        "Einddatumtijd": "2020-01-01T00:00:00.000+00:00",
    }
    with pytest.raises(IOError) as e:
        _send_post_request(url, request=request_toolarge)
    assert "400 Bad Request:" in str(e.value)
    assert '"Succesvol":false' in str(e.value)
    assert (
        '"Foutmelding":"Het maximaal aantal waarnemingen (160000) is overschreden. Beperk uw request."'
        in str(e.value)
    )
    assert '"WaarnemingenLijst":[]' in str(e.value)

    request_nodata = dict(request_valid)
    request_nodata["Periode"] = {
        "Begindatumtijd": "2180-01-01T00:00:00.000+00:00",
        "Einddatumtijd": "2180-01-02T00:00:00.000+00:00",
    }
    with pytest.raises(NoDataError) as e:
        _send_post_request(url, request=request_nodata)
    assert "204 No Content:" in str(e.value)


def test_get_catalogfile_cache():
    catalogfile, use_cache = get_catalogfile_cache(catalog_filter=None)
    assert use_cache is True

    catalogfile, use_cache = get_catalogfile_cache(catalog_filter=[])
    assert use_cache is False


def test_nodataerror(location):
    """
    Test whether a request that returns no data is indeed properly catched also when not
    calling _send_post_request() directly. The response for measurements_slice() is
    identical. The response for measurements_amount() is different because resp.ok=True
    and returns an empty list that is later catched in measurements_amount().
    """
    start_date = dt.datetime(2180, 1, 1)
    end_date = dt.datetime(2180, 4, 1)
    # same response as testing _send_post_request
    with pytest.raises(NoDataError) as e:
        # ddlpy.measurements() catches NoDataError, so we have to test it with _measurements_slice
        _ = ddlpy.ddlpy._measurements_slice(
            location, start_date=start_date, end_date=end_date
        )
    assert "204 No Content: " in str(e.value)
    # different response than testing _send_post_request, since empty result will also raise NoDataError
    with pytest.raises(NoDataError) as e:
        _ = ddlpy.ddlpy.measurements_amount(
            location, start_date=start_date, end_date=end_date
        )
    assert "no measurements available returned" in str(e.value)


def test_locations(locations):
    # check if index is station code
    assert locations.index.name == "Code"
    assert isinstance(locations.index, pd.Index)
    assert isinstance(locations.index[0], str)

    # check presence of columns
    expected_columns = [
        "Locatie_MessageID",
        "Lat",
        "Lon",
        "Coordinatenstelsel",
        "Naam",
        "Omschrijving",
        "Parameter_Wat_Omschrijving",
        "ProcesType",
        "Compartiment.Code",
        "Compartiment.Omschrijving",
        "Grootheid.Code",
        "Grootheid.Omschrijving",
        "Eenheid.Code",
        "Eenheid.Omschrijving",
        "Hoedanigheid.Code",
        "Hoedanigheid.Omschrijving",
        "Parameter.Code",
        "Parameter.Omschrijving",
        "Groepering.Code",
        "Groepering.Omschrijving",
        "Typering.Code",
        "Typering.Omschrijving",
    ]
    for colname in expected_columns:
        assert colname in locations.columns

    # the number of columns depend on the catalog filter in endpoints.json
    assert locations.shape[1] == len(expected_columns)
    # the number of rows is the number of stations, so will change over time
    assert locations.shape[0] > 1

    # check whether first values of all columns have the expected dtype
    for colname in locations.columns:
        if colname in DTYPES_NONSTRING.keys():
            expected_dtype = DTYPES_NONSTRING[colname]
        else:
            expected_dtype = str
        assert isinstance(locations[colname].iloc[0], expected_dtype)

    # check whether all dtypes are the same for entire column
    for colname in locations.columns:
        column_unique_dtypes = locations[colname].apply(type).drop_duplicates()
        assert len(column_unique_dtypes) == 1


def test_locations_extended():
    catalog_filter = [
        "Compartimenten",
        "Eenheden",
        "Grootheden",
        "Hoedanigheden",
        "Groeperingen",
        "MeetApparaten",
        "Typeringen",
        "WaardeBepalingsmethoden",
        "Parameters",
    ]
    locations_extended = ddlpy.locations(catalog_filter=catalog_filter)
    # the number of columns depend on the provided catalog_filter
    assert locations_extended.shape[1] == 25
    # the number of rows is the number of stations, so will change over time
    assert locations_extended.shape[0] > 1


def test_measurements(measurements):
    # check if index is time and check dtype
    assert measurements.index.name == "time"
    assert isinstance(measurements.index, pd.DatetimeIndex)
    assert isinstance(measurements.index[0], pd.Timestamp)

    # check presence of columns, skipping all but one *.Omschrijving and *.Code columns
    expected_columns = [
        "WaarnemingMetadata.Statuswaarde",
        "WaarnemingMetadata.Bemonsteringshoogte",
        "WaarnemingMetadata.Referentievlak",
        "WaarnemingMetadata.OpdrachtgevendeInstantie",
        "WaarnemingMetadata.Kwaliteitswaardecode",
        "Parameter_Wat_Omschrijving",
        "ProcesType",
        "Meetwaarde.Waarde_Alfanumeriek",
        "Meetwaarde.Waarde_Numeriek",
        "Code",
        "Coordinatenstelsel",
        "Naam",
        "Lon",
        "Lat",
        "Grootheid.Code",
        "Grootheid.Omschrijving",
    ]
    for colname in expected_columns:
        assert colname in measurements.columns

    # check the shape of the dataframe
    assert measurements.shape[1] == len(expected_columns) + 32
    assert measurements.shape[0] > 1

    # check whether first values of all columns have the expected dtype
    for colname in measurements.columns:
        if colname in DTYPES_NONSTRING.keys():
            expected_dtype = DTYPES_NONSTRING[colname]
        else:
            expected_dtype = str
        assert isinstance(measurements[colname].iloc[0], expected_dtype)

    # check whether all dtypes are the same for entire column
    for colname in measurements.columns:
        column_unique_dtypes = measurements[colname].apply(type).drop_duplicates()
        assert len(column_unique_dtypes) == 1

    # check whether the filtering was passed properly
    assert set(measurements["ProcesType"].unique()) == {"meting"}


def test_measurements_invalid_to_nan(locations):
    bool_grootheid = locations["Grootheid.Code"] == "WATHTE"
    bool_groepering = locations["Groepering.Code"] == ""
    bool_procestype = locations["ProcesType"] == "meting"
    location = locations[bool_grootheid & bool_groepering & bool_procestype].loc["a12"]

    start_date = dt.datetime(2009, 1, 1)
    end_date = dt.datetime(2009, 4, 1)
    measurements = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date
    )
    qc = measurements["WaarnemingMetadata.Kwaliteitswaardecode"]
    num = measurements["Meetwaarde.Waarde_Numeriek"]
    alf = measurements["Meetwaarde.Waarde_Alfanumeriek"]
    alf_num = alf.astype(float)

    assert "99" in qc.tolist()  # there are invalid values in the dataframe
    assert num.max() < 1000  # but the 999999999.0 have been replaced with nan
    assert num.isnull().any()
    assert alf_num.max() < 1000  # but the 999999999.0 have been replaced with nan
    assert alf_num.isnull().any()
    assert np.allclose(num, alf_num, equal_nan=True)


def test_measurements_freq_yearly(location, measurements):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements_yearly = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date, freq=dateutil.rrule.YEARLY
    )
    assert measurements.shape == measurements_yearly.shape


def test_measurements_freq_none(location, measurements):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements_monthly = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date, freq=None
    )
    assert measurements.shape == measurements_monthly.shape


def test_measurements_available(location):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    data_present = ddlpy.measurements_available(
        location, start_date=start_date, end_date=end_date
    )
    assert data_present is True


def test_measurements_available_false(location):
    # request period for which data is not available
    start_date = dt.datetime(2050, 1, 1)
    end_date = dt.datetime(2050, 4, 1)
    data_present = ddlpy.measurements_available(
        location, start_date=start_date, end_date=end_date
    )
    assert data_present is False


def test_measurements_amount(location):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 5)
    data_amount_dag = ddlpy.measurements_amount(
        location, start_date=start_date, end_date=end_date, period="Dag"
    )
    assert data_amount_dag.shape[0] > 50
    assert data_amount_dag.index.str.len()[0] == 10
    data_amount_maand = ddlpy.measurements_amount(
        location, start_date=start_date, end_date=end_date, period="Maand"
    )
    assert data_amount_maand.shape[0] == 4
    assert data_amount_maand.index.str.len()[0] == 7
    data_amount_jaar = ddlpy.measurements_amount(
        location, start_date=start_date, end_date=end_date, period="Jaar"
    )
    assert data_amount_jaar.shape[0] == 1
    assert data_amount_jaar.index.str.len()[0] == 4


def test_measurements_amount_invalidperiod(location):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 5)
    with pytest.raises(ValueError) as e:
        _ = ddlpy.measurements_amount(
            location, start_date=start_date, end_date=end_date, period="invalid"
        )
    assert "period should be one of ['Jaar', 'Maand', 'Dag']" in str(e.value)


def test_measurements_amount_multipleblocks(location):
    # in 1993 the WaardeBepalingsmethode changes from
    # other:F001 (Rekenkundig gemiddelde waarde over vorige 10 minuten) to
    # other:F007 (Rekenkundig gemiddelde waarde over vorige 5 en volgende 5 minuten)
    date_min = "1990-01-01"
    date_max = "1995-01-01"
    # if we pass one row to the measurements function you can get all the measurements
    df_amount = ddlpy.measurements_amount(location, date_min, date_max)

    index_expected = np.array(["1990", "1991", "1992", "1993", "1994", "1995"])
    values_expected = np.array([52554, 52560, 52704, 52560, 52560, 7])
    assert (df_amount.index == index_expected).all()
    assert (df_amount["AantalMetingen"].values == values_expected).all()


def test_measurements_latest(location):
    """measurements for a location"""
    latest = ddlpy.measurements_latest(location)
    assert latest.shape[0] > 1


def test_measurements_empty(location):
    """measurements for a location"""
    start_date = dt.datetime(2153, 1, 1)
    end_date = dt.datetime(2153, 1, 2)
    measurements = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date
    )
    assert measurements.empty


def test_measurements_typerror(locations):
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    with pytest.raises(TypeError) as e:
        _ = ddlpy.measurements(locations, start_date=start_date, end_date=end_date)
    assert (
        "The provided location is a pandas.DataFrame, but should be a pandas.Series"
        in str(e.value)
    )


def test_measurements_noindex(location):
    # pandas dataframe with Code as column instead of index
    locations_noindex = pd.DataFrame(location).T
    locations_noindex.index.name = "Code"
    locations_noindex = locations_noindex.reset_index(drop=False)

    # normal subsetting and retrieving
    location_sel = locations_noindex.iloc[0]
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(
        location_sel, start_date=start_date, end_date=end_date
    )
    assert measurements.shape[0] > 1


def test_measurements_long(location):
    """measurements for a location"""
    start_date = dt.datetime(1951, 11, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date
    )
    assert measurements.shape[0] > 1


def test_measurements_sorted(measurements):
    """https://github.com/deltares/ddlpy/issues/27"""

    # restore Tijdstip column to avoid error on removal
    measurements = measurements.copy()
    measurements["Tijdstip"] = measurements.index
    # sort dataframe on values so it will not be sorted on time
    meas_wrongorder = measurements.sort_values("Meetwaarde.Waarde_Numeriek")
    assert meas_wrongorder.index.is_monotonic_increasing is False
    meas_clean = ddlpy.ddlpy._clean_dataframe(meas_wrongorder)
    assert meas_clean.index.is_monotonic_increasing is True
    # assert meas_clean.index.duplicated().sum() == 0

    # check wheter indexes are DatetimeIndex
    assert isinstance(meas_wrongorder.index, pd.DatetimeIndex)
    assert isinstance(meas_clean.index, pd.DatetimeIndex)


def test_measurements_duplicated(measurements):
    """
    WALSODN 2010 contains all values three times, ddlpy drops duplicates
    https://github.com/deltares/ddlpy/issues/24

    Tijdstip column and length assertion of meas_clean are important
    to prevent too much duplicates removal https://github.com/deltares/ddlpy/issues/53
    """
    # restore Tijdstip column to avoid too much duplicates removal
    measurements = measurements.copy()
    measurements["Tijdstip"] = measurements.index

    # deliberately duplicate values in a measurements dataframe
    meas_duplicated = pd.concat([measurements, measurements, measurements], axis=0)
    meas_clean = ddlpy.ddlpy._clean_dataframe(meas_duplicated)
    assert len(meas_duplicated) == 3024
    assert len(meas_clean) == len(measurements) == 1008

    # check wheter indexes are DatetimeIndex
    assert isinstance(meas_duplicated.index, pd.DatetimeIndex)
    assert isinstance(meas_clean.index, pd.DatetimeIndex)


def test_measurements_timezone_behaviour(location):
    start_date = "2015-01-01 00:00:00 +01:00"
    end_date = "2015-01-03 00:00:00 +01:00"
    measurements = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date
    )
    assert str(measurements.index[0].tz) == "UTC+01:00"
    assert measurements.index[0] == pd.Timestamp(start_date)
    assert measurements.index[-1] == pd.Timestamp(end_date)

    data_amount_dag = ddlpy.measurements_amount(
        location, start_date=start_date, end_date=end_date, period="Dag"
    )
    # when retrieving with tzone +01:00 we expect 1 value on 2015-01-03
    assert np.allclose(data_amount_dag["AantalMetingen"].values, [144, 144, 1])

    start_date = "2015-01-01"
    end_date = "2015-01-03"
    measurements = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date
    )
    assert str(measurements.index[0].tz) == "UTC+01:00"
    assert measurements.index[0] == pd.Timestamp(start_date).tz_localize(
        "UTC"
    ).tz_convert("UTC+01:00")
    assert measurements.index[-1] == pd.Timestamp(end_date).tz_localize(
        "UTC"
    ).tz_convert("UTC+01:00")

    data_amount_dag = ddlpy.measurements_amount(
        location, start_date=start_date, end_date=end_date, period="Dag"
    )
    # when retrieving with tzone +00:00 we expect 7 values on 2015-01-03
    assert np.allclose(data_amount_dag["AantalMetingen"].values, [138, 144, 7])


datetype_list = ["string", "pd.Timestamp", "dt.datetime", "mixed"]


@pytest.mark.parametrize("datetype", datetype_list)
def test_check_convert_dates(datetype):
    if datetype == "string":
        start_date = "1953-01-01"
        end_date = "1953-04-01"
    elif datetype == "pd.Timestamp":
        start_date = pd.Timestamp("1953-01-01")
        end_date = pd.Timestamp("1953-04-01")
    elif datetype == "dt.datetime":
        start_date = dt.datetime(1953, 1, 1)
        end_date = dt.datetime(1953, 4, 1)
    elif datetype == "mixed":
        start_date = "1953-01-01"
        end_date = dt.datetime(1953, 4, 1)

    # assert output
    start_date_out, end_date_out = ddlpy.ddlpy._check_convert_dates(
        start_date, end_date
    )
    assert start_date_out == "1953-01-01T00:00:00.000+00:00"
    assert end_date_out == "1953-04-01T00:00:00.000+00:00"


def test_check_convert_wrongorder():
    start_date = "1953-01-01"
    end_date = "1953-04-01"

    # assert output
    with pytest.raises(ValueError):
        start_date_out, end_date_out = ddlpy.ddlpy._check_convert_dates(
            end_date, start_date
        )


def test_simplify_dataframe(measurements):
    """
    should be in test_utils.py
    """
    assert len(measurements.columns) == 48
    meas_simple = ddlpy.simplify_dataframe(measurements)
    assert hasattr(meas_simple, "attrs")
    # TODO: the below should be 47 and 1, but there are still RIKZ_WAT instances in
    # OpdrachtgevendeInstantie column, which is different from RIKZMON_WAT
    # this also probably partly causes the 96 duplicated timestamps
    # https://github.com/Rijkswaterstaat/WaterWebservices/issues/16
    assert len(meas_simple.attrs) == 46
    assert len(meas_simple.columns) == 2
    expected_columns = [
        "WaarnemingMetadata.OpdrachtgevendeInstantie",
        "Meetwaarde.Waarde_Numeriek",
    ]
    assert set(meas_simple.columns) == set(expected_columns)


def test_simplify_dataframe_always_preserve(measurements):
    """
    should be in test_utils.py
    """
    assert len(measurements.columns) == 48
    always_preserve = [
        "WaarnemingMetadata.Statuswaarde",
        "WaarnemingMetadata.OpdrachtgevendeInstantie",
        "WaarnemingMetadata.Kwaliteitswaardecode",
        "Groepering.Code",
        "BemonsteringsApparaat.Code",
        "Meetwaarde.Waarde_Numeriek",
    ]
    meas_simple = ddlpy.simplify_dataframe(
        measurements, always_preserve=always_preserve
    )
    assert hasattr(meas_simple, "attrs")
    assert len(meas_simple.attrs) == 42
    assert len(meas_simple.columns) == 6
    expected_columns = [
        "WaarnemingMetadata.Statuswaarde",
        "WaarnemingMetadata.OpdrachtgevendeInstantie",
        "WaarnemingMetadata.Kwaliteitswaardecode",
        "Groepering.Code",
        "BemonsteringsApparaat.Code",
        "Meetwaarde.Waarde_Numeriek",
    ]
    assert set(meas_simple.columns) == set(expected_columns)


def test_simplify_dataframe_always_preserve_invalid_key(measurements):
    """
    should be in test_utils.py
    """
    assert len(measurements.columns) == 48
    always_preserve = ["invalid_key"]
    with pytest.raises(ValueError) as e:
        _ = ddlpy.simplify_dataframe(measurements, always_preserve=always_preserve)
    assert "column 'invalid_key' not present in dataframe" in str(e.value)


def test_simplify_dataframe_alfanumeriek_with_nan_dropped(locations):
    bool_grootheid = locations["Grootheid.Code"] == "WATHTE"
    bool_groepering = locations["Groepering.Code"] == ""
    bool_procestype = locations["ProcesType"] == "meting"
    location = locations[bool_grootheid & bool_groepering & bool_procestype].loc["a12"]

    start_date = dt.datetime(2009, 1, 1)
    end_date = dt.datetime(2009, 4, 1)
    measurements = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date
    )
    meas_simple = ddlpy.simplify_dataframe(df=measurements)
    expected_columns = [
        "WaarnemingMetadata.Kwaliteitswaardecode",
        "Meetwaarde.Waarde_Numeriek",
    ]
    assert set(meas_simple.columns) == set(expected_columns)


def test_dataframe_to_xarray(measurements):
    """
    should be in test_utils.py
    """
    always_preserve = [
        "WaarnemingMetadata.Statuswaarde",
        "WaarnemingMetadata.Kwaliteitswaardecode",
        "MeetApparaat.Code",
        "WaardeBepalingsMethode.Code",
        "Meetwaarde.Waarde_Numeriek",
    ]
    ds_clean = ddlpy.dataframe_to_xarray(
        df=measurements,
        always_preserve=always_preserve,
    )

    non_constant_columns = [
        "WaarnemingMetadata.OpdrachtgevendeInstantie",
        "Meetwaarde.Waarde_Numeriek",
    ]

    preserved = always_preserve + non_constant_columns

    for varname in measurements.columns:
        # check if all varnames in always_preserve and non-constant columns are indeed preserved as variables
        if varname in preserved:
            assert varname in ds_clean.data_vars
            assert varname not in ds_clean.attrs.keys()
        else:
            assert varname not in ds_clean.data_vars
            assert varname in ds_clean.attrs.keys()
            varname_oms = varname.replace(".Code", ".Omschrijving")
            assert varname_oms in ds_clean.attrs.keys()

    # check if times and timezone are correct
    refdate_utc = measurements.tz_convert(None).index[0]
    ds_firsttime = ds_clean.time.to_pandas().iloc[0]
    assert refdate_utc == ds_firsttime
    assert ds_firsttime.tz is None


def test_dataframe_to_xarray_drop_omschrijving(measurements):
    """
    in case of non-unique Code/Omschrijving pairs, the Omschrijving variable should be
    dropped also. The information it contains is added as attrs to the Code value.
    """
    # make MeetApparaat non-unique
    measurements.loc["1953-01-01 02:40:00+01:00", "MeetApparaat.Code"] = "newcode"
    measurements.loc["1953-01-01 02:40:00+01:00", "MeetApparaat.Omschrijving"] = (
        "newoms"
    )

    always_preserve = [
        "WaarnemingMetadata.Statuswaarde",
        "WaarnemingMetadata.Kwaliteitswaardecode",
        "WaardeBepalingsMethode.Code",
        "Meetwaarde.Waarde_Numeriek",
    ]

    ds = ddlpy.dataframe_to_xarray(measurements, always_preserve=always_preserve)
    for varn in ds.data_vars:
        assert not varn.endswith(".Omschrijving")

    expected_attrs = {"newcode": "newoms", "10272": "other:Vlotterniveaumeter"}
    assert ds["MeetApparaat.Code"].attrs == expected_attrs


def test_code_description_attrs_from_dataframe_prevent_empty(measurements):
    """
    should be in test_utils.py
    https://github.com/Deltares/ddlpy/issues/156
    """
    assert "" in measurements["Groepering.Code"].unique()
    attr_dict = ddlpy.utils.code_description_attrs_from_dataframe(measurements)
    for attr_key_value_pairs in attr_dict.values():
        assert "" not in attr_key_value_pairs.keys()
