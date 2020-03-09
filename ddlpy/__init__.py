# -*- coding: utf-8 -*-

"""Top-level package for Data Distributie Laag. Service from Rijkswaterstaat for distributing water quantity data.."""

__author__ = """Fedor Baart"""
__email__ = 'fedor.baart@deltares.nl'
__version__ = '0.1.0'

from ddlpy.ddlpy import locations
from ddlpy.ddlpy import measurements

__all__ = ['locations', 'measurements']
