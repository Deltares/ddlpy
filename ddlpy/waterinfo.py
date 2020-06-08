import pandas as pd
import xarray as xr
from datetime import datetime
import pytz

def waterinfo_read(f, tzone='CET'):
    """Load RWS csv data of  https://waterinfo.rws.nl.

    Load csv downloaded from
    https://waterinfo.rws.nl
    as xarray that can be transformed into a dataframe
     
    TIMEZONE
    The time is converted to 'UTC' from 'CET' (default).
    To ignore timezone conversion, use tzone=None.

    NB according to helpdeskwater: the timezone for downloads
    is always the Dutch legal time at the time of downloading
    (e.g. CET (UTC+2) when downloading between march and 
    october, and UTC+1) rest of the year) whereas the historic
    % data download in the website part (via "Download meer data" )
    are always UTC+1 (no Daylight Saving Time applied).     

    >> ds = waterinfo_read('x.csv',tzone='CET')
    >> df = ds.to_dataframe()
    >> df.head()
     """    
    #Datum;Tijd;Parameter;Locatie;Meting;Verwachting;Astronomisch getijden;Eenheid;Bemonsteringshoogte;Referentievlak;
    #5-5-2020;21:10:00;Waterhoogte Oppervlaktewater t.o.v. Normaal Amsterdams Peil in cm;Den Helder;-1;;;cm;-999999999;NAP;
    df = pd.read_csv(f,delimiter=';')
    
    # handle trailing ;
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # parse time
    t = [datetime.strptime(t,'%d-%m-%Y%H:%M:%S') for t in df['Datum']+df['Tijd']]
            
    # units
    if tzone:

        # all RWS data seems to be CET, local timezone
        t = [t1.replace(tzinfo=pytz.timezone(tzone)).astimezone(pytz.timezone('UTC')) for t1 in t]
        t = [t1.replace(tzinfo=None) for t1 in t] # make datetime64 again
    
    data = df['Meting']
    
    # unit conversoin to SI
    # LUT = {'in':['cm'],'out':['m'],'f':[0.01]}

    atts = {'name':list(set(df['Parameter'])),
           'location':set(df['Locatie'])}

    # The array values in a DataArray have a single (homogeneous) data type.
    # To work with heterogeneous or structured data types in xarray, use coordinates, 
    # or put separate DataArray objects in a single Dataset (see below).
    # ds2 = xr.DataArray(data, coords=[t], dims=['time'])

    ds = xr.Dataset(
        {"data": (("time"), data)},     
        {'time': t})

    # propagate mdatadata
    ds.attrs['name'] = 'zwl'
    for key in df.keys():
        value = set(df[key])
        if len(value) == 1:
            ds['data'].attrs[key] = list(value)[0]
        else:
            ds['data'].attrs[key] = []
            
    ds['data'].attrs['units'] = ds['data'].attrs['Eenheid']
    
    ds['time'].attrs['timezone(original raw)'] = tzone
    if tzone:
        ds['time'].attrs['timezone'] = 'UTC'

    return ds

def exceedance(h, binsize):

    # let lowest bin start below lowest value
    nlb = int(divmod(min(h),binsize)[0])

    # let lowest bin end above hightes value
    nub = int(divmod(max(h),binsize)[0]+2) # 1 extra for range()

    bins = [i*binsize for i in range(nlb,nub)]
    # labels = [bins[i]/2+bins[i+1]/2 for i in range(len(bins)-1)]
    hm = pd.cut(h, bins=bins).value_counts()
    hm = hm.to_frame()
    hm.sort_index(inplace=True, ascending=False)
    hm['lower_bound'] = bins[:-1]
    hm['upper_bound'] = bins[1:]
    hm['cumsum']=hm['h'].cumsum()
    hm['cdf']=hm['cumsum']/max(hm['cumsum'])
    hm.sort_index(inplace=True, ascending=True)

    cdf = hm[['lower_bound','cdf']]
    cdf.set_index('lower_bound',inplace=True)
    return cdf