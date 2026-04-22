# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 09:56:57 2026

@author: veenstra
"""
import pytest
import ddlpy
import datetime as dt


@pytest.fixture
def endpoints():
    """
    Get the endpoints from the api
    """
    endpoints = ddlpy.ddlpy.ENDPOINTS
    return endpoints


@pytest.fixture
def locations():
    """return all locations"""
    locations = ddlpy.locations()
    return locations


@pytest.fixture
def location(locations):
    """return sample location"""
    bool_grootheid = locations["Grootheid.Code"] == "WATHTE"
    bool_groepering = locations["Groepering.Code"] == ""
    bool_procestype = locations["ProcesType"] == "meting"
    location = locations[bool_grootheid & bool_groepering & bool_procestype].loc[
        "denhelder.marsdiep"
    ]
    return location


@pytest.fixture
def measurements(location):
    """measurements for a location"""
    start_date = dt.datetime(1953, 1, 1)
    end_date = dt.datetime(1953, 4, 1)
    measurements = ddlpy.measurements(
        location, start_date=start_date, end_date=end_date
    )
    return measurements
