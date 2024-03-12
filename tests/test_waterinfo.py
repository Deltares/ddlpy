# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 15:33:59 2024

@author: veenstra
"""

from ddlpy.waterinfo import waterinfo_read
import os


def test_waterinfo_read():
    # example in May, during DST
    folder = r'c:\DATA\ddlpy\tests'
    f = os.path.join(folder,'20200608_069_20200507.csv')
    g = os.path.join(folder,'NVT_WATHTE_SCHE_20200507.csv')
    
    dxf_list = waterinfo_read(f)
    dxg = waterinfo_read(g)
    
    dxf0 = dxf_list[0]
    assert "time" in dxf0.variables
    assert "data" in dxf0.variables
    assert "time" in dxg.variables
    assert "data" in dxg.variables
