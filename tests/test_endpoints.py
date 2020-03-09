#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddlpy` package."""

import pytest

import requests

from ddlpy import ddlpy


@pytest.fixture
def endpoints():
    """
    Get the endpoints from the api
    """
    return ddlpy.ENDPOINTS

@pytest.fixture
def collect_catalogue_resp(endpoints):
    endpoint = endpoints['collect_catalogue']
    resp = requests.post(endpoint['url'], json=endpoint['request'])
    return resp

def test_collect_catalogue(collect_catalogue_resp):
    assert collect_catalogue_resp.status_code == 200


@pytest.fixture
def collect_observations_resp(endpoints):
    endpoint = endpoints['collect_observations']
    resp = requests.post(endpoint['url'], json=endpoint['request'])
    return resp

def test_collect_observations(collect_observations_resp):
    assert collect_observations_resp.status_code == 200


@pytest.fixture
def collect_latest_observations_resp(endpoints):
    endpoint = endpoints['collect_latest_observations']
    resp = requests.post(endpoint['url'], json=endpoint['request'])
    return resp

def test_collect_latest_observations(collect_latest_observations_resp):
    assert collect_latest_observations_resp.status_code == 200


@pytest.fixture
def check_observations_available_resp(endpoints):
    endpoint = endpoints['check_observations_available']
    resp = requests.post(endpoint['url'], json=endpoint['request'])
    return resp

def test_check_observations_available(check_observations_available_resp):
    assert check_observations_available_resp.status_code == 200

@pytest.fixture
def collect_number_of_observations_resp(endpoints):
    endpoint = endpoints['collect_number_of_observations']
    resp = requests.post(endpoint['url'], json=endpoint['request'])
    return resp

def test_collect_number_of_observations(collect_number_of_observations_resp):
    assert collect_number_of_observations_resp.status_code == 200

@pytest.fixture
def request_bulk_observations_resp(endpoints):
    endpoint = endpoints['request_bulk_observations']
    resp = requests.post(endpoint['url'], json=endpoint['request'])
    return resp

def test_request_bulk_observations(request_bulk_observations_resp):
    assert request_bulk_observations_resp.status_code == 200
