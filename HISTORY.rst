=======
History
=======

0.7.0 (2025-06-12)
------------------
* resolved datetime parsing warning by providing datetime format in https://github.com/Deltares/ddlpy/pull/131

0.6.0 (2024-10-08)
------------------
* avoid timezone conversion if tz-naive `ddlpy.dataframe_to_xarray` in https://github.com/Deltares/ddlpy/pull/106
* added some missing dependencies in https://github.com/Deltares/ddlpy/pull/108
* `ddlpy.measurements_amount()` now returns all amounts in https://github.com/Deltares/ddlpy/pull/115

0.5.0 (2024-04-26)
------------------
* avoid duplicated periods in dataframe returned by `ddlpy.measurements_amount()` in https://github.com/Deltares/ddlpy/pull/93
* allow for different retrieval frequencies (including None) in `ddlpy.measurements()` in https://github.com/Deltares/ddlpy/pull/95
* only catch "Geen gegevens gevonden!" error message and raise all others (for instance for a too large request) in https://github.com/Deltares/ddlpy/pull/97
* support for timezones in start_date/end_date in https://github.com/Deltares/ddlpy/pull/98

0.4.0 (2024-04-08)
------------------
* added `catalog_filter` argument to `ddlpy.locations()` to enabling retrieving the extended catalog in https://github.com/Deltares/ddlpy/pull/87
* pass all Code parameters to measurements request instead of only four in https://github.com/Deltares/ddlpy/pull/88
* added `ddlpy.dataframe_to_xarray()` function in https://github.com/Deltares/ddlpy/pull/86

0.3.0 (2024-03-13)
------------------
* improved nan filtering of measurements in https://github.com/deltares/ddlpy/pull/30
* add `ddlpy.measurements_available()` check in https://github.com/deltares/ddlpy/pull/33 and https://github.com/deltares/ddlpy/pull/58
* add `ddlpy.measurements_latest()` to retrieve latest measurements in https://github.com/deltares/ddlpy/pull/35
* add optional time-sorting of returned measurements dataframe and made drop_duplicates optional in https://github.com/deltares/ddlpy/pull/37
* add support for time strings in addition to `pd.Timestamp` and `dt.datetime` in https://github.com/deltares/ddlpy/pull/41
* add `ddlpy.simplify_dataframe()` function which drops constant columns and adds the properties as attrs in https://github.com/deltares/ddlpy/pull/43
* consistency improvements for `ddlpy.measurements()` output dataframe in https://github.com/deltares/ddlpy/pull/45
* add distinction for Groepering (timeseries vs. extremes) to `ddlpy.locations()` dataframe in https://github.com/deltares/ddlpy/pull/49
* drop `Tijdstip` column in `ddlpy.measurements()` output dataframe to avoid duplication with time index in https://github.com/deltares/ddlpy/pull/52 and https://github.com/deltares/ddlpy/pull/54
* add `ddlpy.measurements_amount()` to retrieve the number of available measurements grouped by day/month/year in https://github.com/Deltares/ddlpy/pull/63
* catch accidentally switched start/end dates in https://github.com/Deltares/ddlpy/pull/65
* in case of no measurements, return empty dataframe instead of None or empty list in https://github.com/Deltares/ddlpy/pull/75

0.1.0 (2019-01-03)
------------------
* First release on PyPI.
