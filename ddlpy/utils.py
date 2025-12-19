import dateutil.rrule
import itertools
import pandas as pd
import numpy as np


def date_series(start, end, freq=dateutil.rrule.MONTHLY):
    """return a list of start and end date over the timespan start[->end following the frequency rule"""

    def pairwise(it):
        """return all sequential pairs"""
        # loop over the iterator twice.
        # tee it so we don't consume it twice
        it0, it1 = itertools.tee(it)
        i0 = itertools.islice(it0, None)
        i1 = itertools.islice(it1, 1, None)
        # merge to a list of pairs
        return zip(i0, i1)

    # go over the rrule, also include the end, return consequitive pairs
    result = list(
        pairwise(
            list(dateutil.rrule.rrule(dtstart=start, until=end, freq=freq)) + [end]
        )
    )
    # remove last one if empty (first of month until first of month)
    if len(result) > 1 and result[-1][0] == result[-1][1]:
        # remove it
        del result[-1]
    return result


def simplify_dataframe(df: pd.DataFrame, always_preserve=[]):
    """
    Drop columns with constant values from the dataframe and collect them
    in a dictionary which is added as attrs of the dataframe.
    The column Meetwaarde.Waarde_Alfanumeriek is also dropped if it is a duplicate of
    Meetwaarde.Waarde_Numeriek.
    The column names passed in `always_preserve` are preserved even if they are constant.
    """

    # define which columns are constant
    bool_constant = (df == df.iloc[0]).all(axis=0)

    # drop Waarde_Alfanumeriek if duplicate of Waarde_Numeriek
    str_num = "Meetwaarde.Waarde_Numeriek"
    str_alf = "Meetwaarde.Waarde_Alfanumeriek"
    if str_num in df.columns and str_alf in df.columns:
        df_num = df[str_num]
        df_alf = df[str_alf].astype(float)
        if np.allclose(df_num, df_alf, equal_nan=True):
            bool_constant[str_alf] = True

    # preserve some columns (even if their values are constant) by setting them as not constant
    for colname in always_preserve:
        if colname not in df.columns:
            raise ValueError(f"column '{colname}' not present in dataframe")
        bool_constant[colname] = False

    # constant columns are flattened and converted to dict of attrs
    df_attrs = df.loc[:, bool_constant].iloc[0].to_dict()

    # varying columns are kept in output dataframe
    df_simple = df.loc[:, ~bool_constant].copy()

    # attach as attrs to dataframe
    df_simple.attrs = df_attrs

    return df_simple


def code_description_attrs_from_dataframe(df: pd.DataFrame):
    # create var_attrs_dict
    colname_code_list = df.columns[df.columns.str.contains(".Code")]
    colname_oms_list = df.columns[df.columns.str.contains(".Omschrijving")]
    var_attrs_dict = {}
    for colname_code, colname_oms in zip(colname_code_list, colname_oms_list):
        meas_twocol = df[[colname_code, colname_oms]].drop_duplicates()
        attr_dict = meas_twocol.set_index(colname_code)[colname_oms].to_dict()
        # drop empty attribute names/keys since these are not supported when writing to netcdf file
        if "" in attr_dict.keys():
            attr_dict.pop("")
        var_attrs_dict[colname_code] = attr_dict
    return var_attrs_dict


def dataframe_to_xarray(df: pd.DataFrame, always_preserve=[]):
    """
    Converts the measurement dataframe to a xarray dataset. The dataframe is first
    simplified with `simplify_dataframe()` to minimize the size of the netcdf dataset on
    disk.

    The timestamps are converted to UTC since xarray does not support non-UTC timestamps.
    These can be converted to different timezones after loading the netcdf and converting
    to a pandas dataframe with df.index.tz_convert().

    Furthermore, all ".Omschrijving" variables are dropped and the information is added
    as attributes to the Code variables.

    When writing the dataset to disk with ds.to_netcdf() it is recommended to use
    `format="NETCDF3_CLASSIC"` or `format="NETCDF4_CLASSIC"` since this automatically
    converts variables of dtype <U to |S which saves a lot of disk space for DDL data.
    """

    df_simple = simplify_dataframe(df, always_preserve=always_preserve)

    # convert to UTC to please xarray/netcdf4 (otherwise we get invalid timestamps)
    # adding a refdate with tzinfo is also possible but adds confusion and timestamps still have to be stored as UTC
    if df_simple.index.tz is not None:
        df_simple.index = df_simple.index.tz_convert(None)

    # convert to xarray dataset and add ds_attrs
    ds = df_simple.to_xarray()
    ds = ds.assign_attrs(df_simple.attrs)

    # assign attrs with code+omschrijving to each *.Code variable
    var_attrs_dict = code_description_attrs_from_dataframe(df)
    for varn in ds.data_vars:
        if varn in var_attrs_dict.keys():
            var_attrs = var_attrs_dict[varn]
            ds[varn] = ds[varn].assign_attrs(var_attrs)

    # drop .Omschrijving variables
    omschrijving_vars = []
    for varn in ds.data_vars:
        if varn.endswith(".Omschrijving"):
            omschrijving_vars.append(varn)
    ds = ds.drop_vars(omschrijving_vars)

    return ds
