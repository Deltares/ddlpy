#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `utils` package."""

import pytest

from ddlpy import utils

import datetime



def test_content():
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    start = datetime.datetime(2018, 1, 1)
    end = datetime.datetime(2018, 3, 1)
    result = utils.date_series(start, end)
    expected = [
        (datetime.datetime(2018, 1, 1, 0, 0), datetime.datetime(2018, 2, 1, 0, 0)),
        (datetime.datetime(2018, 2, 1, 0, 0), datetime.datetime(2018, 3, 1, 0, 0))
    ]
    assert result == expected

    start = datetime.datetime(2017, 11, 15)
    end = datetime.datetime(2018, 3, 5)
    result = utils.date_series(start, end)
    expected = [
        (datetime.datetime(2017, 11, 15, 0, 0), datetime.datetime(2017, 12, 15, 0, 0)),
        (datetime.datetime(2017, 12, 15, 0, 0), datetime.datetime(2018, 1, 15, 0, 0)),
        (datetime.datetime(2018, 1, 15, 0, 0), datetime.datetime(2018, 2, 15, 0, 0)),
        (datetime.datetime(2018, 2, 15, 0, 0), datetime.datetime(2018, 3, 5, 0, 0))
    ]
    assert result == expected
