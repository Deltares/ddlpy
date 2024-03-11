=======
History
=======

UNRELEASED
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

0.1.0 (2019-01-03)
------------------
* First release on PyPI.
