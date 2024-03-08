=======
History
=======

UNRELEASED
------------------
* improved nan filtering of measurements in https://github.com/openearth/ddlpy/pull/30
* add early return when no data in entire requested period in https://github.com/openearth/ddlpy/pull/33
* add `ddlpy.measurements_latest()` to retrieve latest measurements in https://github.com/openearth/ddlpy/pull/35
* add optional time-sorting of returned measurements dataframe and made drop_duplicates optional in https://github.com/openearth/ddlpy/pull/37
* add support for time strings in addition to `pd.Timestamp` and `dt.datetime` in https://github.com/openearth/ddlpy/pull/41
* add `ddlpy.simplify_dataframe()` function which drops constant columns and adds the properties as attrs in https://github.com/openearth/ddlpy/pull/43
* consistency improvements for `ddlpy.measurements()` output dataframe in https://github.com/openearth/ddlpy/pull/45
* add distinction for Groepering (timeseries vs. extremes) to `ddlpy.locations()` dataframe in https://github.com/openearth/ddlpy/pull/49
* drop `Tijdstip` column in `ddlpy.measurements()` output dataframe to avoid duplication with time index in https://github.com/openearth/ddlpy/pull/52

0.1.0 (2019-01-03)
------------------
* First release on PyPI.
