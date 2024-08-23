import dateutil.rrule
import itertools
import pandas as pd


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
            list(
                dateutil.rrule.rrule(dtstart=start, until=end, freq=freq)
            ) + [end]
        )
    )
    # remove last one if empty (first of month until first of month)
    if len(result) > 1 and result[-1][0] == result[-1][1]:
        # remove it
        del result[-1]
    return result


def simplify_dataframe(df: pd.DataFrame):
    """
    Drop columns with constant values from the dataframe and collect them 
    in a dictionary which is added as attrs of the dataframe.
    """
    
    bool_constant = (df == df.iloc[0]).all()
    
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
    var_attrs_dict = {}
    for colname_code in colname_code_list:
        colname_oms = colname_code.replace(".Code",".Omschrijving")
        meas_twocol = df[[colname_code,colname_oms]].drop_duplicates()
        attr_dict = meas_twocol.set_index(colname_code)[colname_oms].to_dict()
        var_attrs_dict[colname_code] = attr_dict
    return var_attrs_dict


def dataframe_to_xarray(df: pd.DataFrame, drop_if_constant=[]):
    """
    Converts the measurement dataframe to a xarray dataset,
    including several cleanups to minimize the size of the netcdf dataset on disk:
    
    - The column 'Parameter_Wat_Omschrijving' is dropped (combination of information in other columns)
    - The column 'Meetwaarde.Waarde_Alfanumeriek' is dropped if 'Meetwaarde.Waarde_Numeriek' is present (contains duplicate values in that case)
    - All Omschrijving columns are dropped and added as attributes to the Code variables
    - All NVT-only Code columns are dropped and added as ds attributes
    - All location columns are dropped and added as ds attributes
    - All drop_if_constant columns are dropped and added as ds attributes (if the values are indeed constant)
    
    The timestamps are converted to UTC since xarray does not support non-UTC timestamps.
    These can be converted to different timezones after loading the netcdf and converting 
    to a pandas dataframe with df.index.tz_convert().

    When writing the dataset to disk with ds.to_netcdf() it is recommended to use
    `format="NETCDF3_CLASSIC"` or `format="NETCDF4_CLASSIC"` since this automatically
    converts variables of dtype <U to |S which saves a lot of disk space for DDL data.
    """

    # create list of columns with duplicate info (often not constant), will be dropped
    cols_bulky = ["Parameter_Wat_Omschrijving"]
    if "Meetwaarde.Waarde_Alfanumeriek" in df.columns and 'Meetwaarde.Waarde_Numeriek' in df.columns:
        # drop alfanumeriek if duplicate of numeriek # TODO: should not be returned by ddl
        cols_bulky.append("Meetwaarde.Waarde_Alfanumeriek")
    
    # create list of all omschrijving columns, will be dropped (added as ds[varn].attrs via code_description_attrs_from_dataframe())
    cols_omschrijving = df.columns[df.columns.str.contains(".Omschrijving")].tolist()
    
    # create list of all-NVT *.Code columns, will be dropped (codes added as ds.attrs)
    bool_onlynvt_code = (df=='NVT').all(axis=0)
    cols_onlynvt_code = df.columns[bool_onlynvt_code].tolist()
    cols_onlynvt_code = [x for x in cols_onlynvt_code if x.endswith(".Code")]
    
    # create list of location columns, will be dropped (added as ds.attrs)
    cols_location = ['Code', 'Naam', 'Coordinatenstelsel', 'X', 'Y']
    
    # add drop_if_constant colums to list if values are indeed constant, will be dropped (added as ds.attrs)
    cols_constant = []
    for colname in drop_if_constant:
        assert colname in df.columns
        if len(df[colname].drop_duplicates()) == 1:
            cols_constant.append(colname)
    
    # create ds attrs for all nvt/location/constant columns
    ds_attrs = {}
    attrs_columns = cols_onlynvt_code + cols_constant + cols_location
    for colname in attrs_columns:
        ds_attrs[colname] = df[colname].iloc[0]
    
    # drop columns 
    drop_columns = (cols_bulky + cols_location + cols_constant +
                    cols_onlynvt_code + cols_omschrijving)
    df_simple = df.drop(drop_columns, axis=1, errors='ignore')
    
    # convert to UTC to please xarray/netcdf4 (otherwise we get invalid timestamps)
    # adding a refdate with tzinfo is also possible but adds confusion and timestamps still have to be stored as UTC
    if df_simple.index.tz is not None:
        df_simple.index = df_simple.index.tz_convert(None)
    
    # convert to xarray dataset and add ds_attrs
    ds = df_simple.to_xarray()
    ds = ds.assign_attrs(ds_attrs)

    # assign attrs with code+omschrijving to each *.Code variable
    var_attrs_dict = code_description_attrs_from_dataframe(df)
    for varn in ds.data_vars:
        if varn in var_attrs_dict.keys():
            var_attrs = var_attrs_dict[varn]
            ds[varn] = ds[varn].assign_attrs(var_attrs)

    return ds
