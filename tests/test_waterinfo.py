# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 15:33:59 2024

@author: veenstra
"""

from ddlpy.waterinfo import waterinfo_read
import os

dir_tests = os.path.dirname(os.path.abspath(__file__))


def test_waterinfo_read():
    # example in May, during DST
    f = os.path.join(dir_tests, "20200608_069_20200507.csv")
    g = os.path.join(dir_tests, "NVT_WATHTE_SCHE_20200507.csv")

    dxf_list = waterinfo_read(f, block=False)
    dxg_list = waterinfo_read(g, block=False)

    dxf0 = dxf_list[0]
    dxg0 = dxg_list[0]
    assert "time" in dxf0.variables
    assert "data" in dxf0.variables
    assert "time" in dxg0.variables
    assert "data" in dxg0.variables

    assert dxf0.time.to_series().index[0].isoformat() == '2020-05-06T23:00:00'
    assert dxf0.time.to_series().index[-1].isoformat() == '2020-05-07T22:50:00'
    assert dxg0.time.to_series().index[0].isoformat() == '2020-05-06T22:00:00'
    assert dxg0.time.to_series().index[-1].isoformat() == '2020-05-07T21:50:00'
