import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
import pytz

    
def waterinfo_read(f, encoding='latin'):
    """Load RWS csv data of https://waterinfo.rws.nl into xarray

    Can handle two types of files
    * direct download from https://waterinfo.rws.nl
      first column is 'Datum'
    * request via https://waterinfo.rws.nl for link per email
      first column is 'MONSTER_IDENTIFICATIE'
      If multiple variables are present, a list of xarrays is returned.
    
    An xarray that can be transformed into a dataframe:
     
    TIMEZONE
    The time is converted to 'UTC' from 
    * 'CET' (default) for direct downloads
    * 'UTC+1' (default) for request per email
    Passing a value in hours is also possible: tzone=.
    To ignore timezone conversion, use tzone=None.
    NB according to helpdeskwater: the timezone for downloads
    is always the Dutch legal time at the time of downloading
    (e.g. CET (UTC+2) when downloading between march and 
    october, and UTC+1) rest of the year) whereas the historic
    % data download in the website part (via "Download meer data" )
    are always UTC+1 (no Daylight Saving Time applied).

    Example:
    >> ds = waterinfo_read('x.csv',tzone='UTC+1')
    >> df = ds.to_dataframe()
    >> df.head()
     """    
    
    dfall = pd.read_csv(f,delimiter=';', encoding=encoding)
    
    if 'WAARNEMINGDATUM' in dfall.keys():
        variablecolumn = 'GROOTHEID_ CODE'
        tzone = 1
        
        dfall = dfall.loc[dfall['KWALITEITSOORDEEL_CODE']=='Normale waarde']
        
    elif 'Datum' in dfall.keys():
        variablecolumn = 'Parameter'
        tzone = 'CET'
        
    variables = list(set(dfall[variablecolumn]))
    
    ds = []
    
    for variable in variables:
        
        df = dfall[dfall[variablecolumn]==variable]
        
        print(len(df),' rows for variable: ',variable)
    
        if 'WAARNEMINGDATUM' in df.keys():
#MONSTER_IDENTIFICATIE;MEETPUNT_IDENTIFICATIE;TYPERING_OMSCHRIJVING;TYPERING_CODE;GROOTHEID_OMSCHRIJVING;GROOTHEID_ CODE;PARAMETER_OMSCHRIJVING;PARAMETER_ CODE;EENHEID_CODE;HOEDANIGHEID_OMSCHRIJVING;HOEDANIGHEID_CODE;COMPARTIMENT_OMSCHRIJVING;COMPARTIMENT_CODE;WAARDEBEWERKINGSMETHODE_OMSCHRIJVING;WAARDEBEWERKINGSMETHODE_CODE;WAARDEBEPALINGSMETHODE_OMSCHRIJVING;WAARDEBEPALINGSMETHODE_CODE;BEMONSTERINGSSOORT_OMSCHRIJVING;BEMONSTERINGSSOORT_CODE;WAARNEMINGDATUM;WAARNEMINGTIJD;LIMIETSYMBOOL;NUMERIEKEWAARDE;ALFANUMERIEKEWAARDE;KWALITEITSOORDEEL_CODE;STATUSWAARDE;OPDRACHTGEVENDE_INSTANTIE;MEETAPPARAAT_OMSCHRIJVING;MEETAPPARAAT_CODE;BEMONSTERINGSAPPARAAT_OMSCHRIJVING;BEMONSTERINGSAPPARAAT_CODE;PLAATSBEPALINGSAPPARAAT_OMSCHRIJVING;PLAATSBEPALINGSAPPARAAT_CODE;BEMONSTERINGSHOOGTE;REFERENTIEVLAK;EPSG;X;Y;ORGAAN_OMSCHRIJVING;ORGAAN_CODE;TAXON_NAME
#;Scheveningen;;;Waterhoogte berekend;WATHTBRKD;;;cm;t.o.v. Normaal Amsterdams Peil;NAP;Oppervlaktewater;OW;;;Astronomische waterhoogte mbv harmonische analyse;other:F012;;;01-05-2020;00:00:00;;-44;;Normale waarde;Ongecontroleerd;RIKZMON_WAT;;;;;;;-999999999;NVT;25831;586550,994420996;5772806,43069697;;;

            t = [datetime.strptime(t,'%d-%m-%Y%H:%M:%S') for t in df['WAARNEMINGDATUM']+df['WAARNEMINGTIJD']]

            data = df['NUMERIEKEWAARDE']/1.

            key_units = 'EENHEID_CODE'

            keys2meta = ['MEETPUNT_IDENTIFICATIE',\
                        'GROOTHEID_OMSCHRIJVING','GROOTHEID_ CODE','EENHEID_CODE',\
                        'HOEDANIGHEID_OMSCHRIJVING','HOEDANIGHEID_CODE',\
                        'COMPARTIMENT_CODE','COMPARTIMENT_OMSCHRIJVING',\
                        'WAARDEBEPALINGSMETHODE_CODE','WAARDEBEPALINGSMETHODE_OMSCHRIJVING',\
                        'KWALITEITSOORDEEL_CODE','STATUSWAARDE','OPDRACHTGEVENDE_INSTANTIE',\
                        'EPSG','X','Y']        

        elif 'Datum' in df.keys():
#Datum;Tijd;Parameter;Locatie;Meting;Verwachting;Astronomisch getijden;Eenheid;Bemonsteringshoogte;Referentievlak;
#5-5-2020;21:10:00;Waterhoogte Oppervlaktewater t.o.v. Normaal Amsterdams Peil in cm;Den Helder;-1;;;cm;-999999999;NAP;

            # handle trailing ;
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

            # parse time
            t = [datetime.strptime(t,'%d-%m-%Y%H:%M:%S') for t in df['Datum']+df['Tijd']]

            data = df['Meting']    
            key_units = 'Eenheid'

            keys2meta = ['Parameter','Locatie','Eenheid','Bemonsteringshoogte','Referentievlak'];

        else:
            print("Unknown file header.")
            raise

        if isinstance(tzone,type('a')):
            # does not apply DST t = [t1.replace(tzinfo=pytz.timezone(tzone)).astimezone(pytz.timezone('UTC')) for t1 in t]
            t = [t1 - pytz.timezone('CET').utcoffset(t1) for t1 in t]
        else:
            t = [t1 - timedelta(seconds=3600)*tzone for t1 in t]
        t = [t1.replace(tzinfo=None) for t1 in t] # make datetime64 again

        # The array values in a DataArray have a single (homogeneous) data type.
        # To work with heterogeneous or structured data types in xarray, use coordinates, 
        # or put separate DataArray objects in a single Dataset (see below).
        # ds2 = xr.DataArray(data, coords=[t], dims=['time'])

        d = xr.Dataset(
            {"data": (("time"), data)},     
            {'time': t}) # make datetime64 again
            
        d.attrs['file.name'] = f
        d.attrs['file.encoding'] = encoding
        d.attrs['file.original_columns'] = df.keys()
        d.attrs['file.original_timezone'] = tzone

        # unit conversoin to SI
        # LUT = {'in':['cm'],'out':['m'],'f':[0.01]}

        for key in keys2meta:
            value = set(df[key])
            if len(value) == 1:
                d['data'].attrs[key] = list(value)[0]
            else:
                d['data'].attrs[key] = value

        d['data'].attrs['units'] = d['data'].attrs[key_units]

        if tzone:
            d['time'].attrs['timezone'] = 'UTC'
            
        ds.append(d)
        
    if len(ds)==1:
        ds = ds[0]

    return ds
