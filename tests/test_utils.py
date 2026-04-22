#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `utils` package."""

from ddlpy.utils import date_series
import datetime as dt
import ddlpy
import pytest


def test_date_series():
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    start = dt.datetime(2018, 1, 1)
    end = dt.datetime(2018, 3, 1)
    result = date_series(start, end)
    expected = [
        (dt.datetime(2018, 1, 1, 0, 0), dt.datetime(2018, 2, 1, 0, 0)),
        (dt.datetime(2018, 2, 1, 0, 0), dt.datetime(2018, 3, 1, 0, 0)),
    ]
    assert result == expected

    start = dt.datetime(2017, 11, 15)
    end = dt.datetime(2018, 3, 5)
    result = date_series(start, end)
    expected = [
        (dt.datetime(2017, 11, 15, 0, 0), dt.datetime(2017, 12, 15, 0, 0)),
        (dt.datetime(2017, 12, 15, 0, 0), dt.datetime(2018, 1, 15, 0, 0)),
        (dt.datetime(2018, 1, 15, 0, 0), dt.datetime(2018, 2, 15, 0, 0)),
        (dt.datetime(2018, 2, 15, 0, 0), dt.datetime(2018, 3, 5, 0, 0)),
    ]
    assert result == expected


def test_simplify_dataframe(measurements):
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


def test_dataframe_to_xarray_to_netcdf(measurements, tmp_path):
    ds_clean = ddlpy.dataframe_to_xarray(
        df=measurements,
    )
    file_out = tmp_path / "test_default.nc"
    ds_clean.to_netcdf(file_out, engine=None)
    file_out = tmp_path / "test_h5netcdf.nc"
    ds_clean.to_netcdf(file_out, engine="h5netcdf")
    file_out = tmp_path / "test_netcdf4.nc"
    ds_clean.to_netcdf(file_out, engine="netcdf4")
    file_out = tmp_path / "test_netcdf4_classic.nc"
    ds_clean.to_netcdf(file_out, engine="netcdf4", format="NETCDF4_CLASSIC")


def test_code_description_attrs_from_dataframe_prevent_empty(measurements):
    """
    https://github.com/Deltares/ddlpy/issues/156
    """
    assert "" in measurements["Groepering.Code"].unique()
    attr_dict = ddlpy.utils.code_description_attrs_from_dataframe(measurements)
    for attr_key_value_pairs in attr_dict.values():
        assert "" not in attr_key_value_pairs.keys()
