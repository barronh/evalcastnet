import pandas as pd
import numpy as np
from datetime import datetime
from netCDF4 import Dataset
import sys

sitepath, datapath, outpath = sys.argv[1:]
_alldates = {}

dfmts = {
    '/': '%m/%d/%Y %H:%M:%S',
    '-': '%Y-%m-%d %H:%M:%S'
}
dfmt = None

def cacheddate(dstr):
    global dfmt
    if dstr in _alldates:
        return _alldates[dstr]
    if dfmt is None:
        if '/' in dstr:
            dfmt = dfmts['/']
        elif '-' in dstr:
            dfmt = dfmts['-']
        else:
            raise ValueError('Unknown format: {}; must be in {}'.format(dstr, list(dfmts.values())))

    out = _alldates[dstr] = datetime.strptime(dstr, dfmt)
    return out

data = pd.read_csv(datapath, parse_dates = ['DATE_TIME'], date_parser = cacheddate, dtype = dict(QA_CODE = str))
data = data.query('QA_CODE in ("1", "2", "3")')

site = pd.read_csv(sitepath, dtype = dict(SITE_NUM = int))
site = site[site.SITE_ID.isin(data.SITE_ID)]
def tzoffset(key):
    """
    simple timeshift needs checking
    """
    if key.startswith('EA'): off = -5
    if key.startswith('CE'): off = -6
    if key.startswith('MO'): off = -7
    if key.startswith('PA'): off = -8
    if key.startswith('AL'): off = -9
    return off


site['TIME_OFFSET'] = pd.Series([tzoffset(tzn) for tzn in site.TIME_ZONE.values], index = site.index)
refdate = np.datetime64('1970-01-01', '[ns]')
startdate = np.datetime64('2016-01-01 00:00:00', '[ns]')
enddate = np.datetime64('2017-01-01 00:00:00', '[ns]')
sites = data['SITE_ID']
usites = site['SITE_ID']
usites = site['SITE_ID']

uqa = np.unique(data['QA_CODE'].values)

outf = Dataset(outpath, 'w')
outf.createDimension('time', None)
outf.createDimension('nv', 2)
outf.createDimension('site', site.shape[0])
outf.createDimension('NAMELEN', 6)
outf.SITENAMES = '|'.join(site['SITE_ID'].values)

sitev = outf.createVariable('site', 'i', ('site',))
sitev.description = 'CASTNET SITE_NUM'
sitev.units = 'none'
sitev[:] = site['SITE_NUM'].values

siteidv = outf.createVariable('site_id', 'c', ('site','NAMELEN'))
siteidv.description = 'CASTNET SITE_ID'
siteidv.units = 'none'
siteidv[:] = np.array(site['SITE_ID'].values, dtype = 'S6').view('S1')

latv = outf.createVariable('latitude', 'f', ('site',))
latv.units = 'degrees'
latv[:] = site['LATITUDE'].values

lonv = outf.createVariable('longitude', 'f', ('site',))
lonv.units = 'degrees'
lonv[:] = site['LONGITUDE'].values

elevv = outf.createVariable('elevation', 'f', ('site',))
elevv.units = 'm'
elevv[:] = site['ELEVATION'].values

timev = outf.createVariable('time', 'd', ('time',))
timev.units = 'hours since 1970-01-01 00:00:00Z'
timev[:] = np.arange(int((enddate - startdate) / 3600e9)) + (startdate - refdate) / 3600e9
timev[:] += 0.5

timebv = outf.createVariable('time_bounds', 'd', ('time', 'nv'))
timebv.units = 'hours since 1970-01-01 00:00:00Z'
timebv[:, 0] = timev[:] - 0.5
timebv[:, 1] = timev[:] + 0.5

ntimes = timev.size
o3v = outf.createVariable('O3', 'f', ('time', 'site'), fill_value = -999.)
o3v.units = 'ppb'
o3v.missing_value = -999.

qav = outf.createVariable('O3_QA', 'f', ('time', 'site'), fill_value = -999)
qav.units = '1 or 3'
qav.missing_value = -999
o3tmp = np.ma.masked_all(o3v.shape, dtype = 'f')
qatmp = np.ma.masked_all(o3v.shape, dtype = 'f')
sitelist = sitev[:].tolist()
for ri, row in site.iterrows():
    sitenum = row['SITE_NUM']
    siteidx = sitelist.index(sitenum)
    siteid  = row['SITE_ID']
    tzoff = row['TIME_OFFSET']
    print(sitenum, siteid, siteidx)
    sitedata = data[data.SITE_ID == siteid]
    if not sitedata.shape[0] == 0:
        sitedates = sitedata['DATE_TIME'] - np.timedelta64(tzoff*3600, 's')
        reldates = sitedates - startdate
        hoursss = (reldates.values / 3600e9).astype('i')
        inyear = (hoursss > 0) & (hoursss <= ntimes)
        print(inyear.sum())
        timeidx = hoursss[inyear]
        siteyeardata = sitedata[inyear]
        o3tmp[timeidx, siteidx] = np.ma.masked_invalid(siteyeardata['OZONE'].values)
        qatmp[timeidx, siteidx] = np.ma.masked_invalid(siteyeardata['QA_CODE'].values.astype('i'))
o3v[:] = o3tmp[:]
qav[:] = qatmp[:]
outf.close()
#"SITE_ID","DATE_TIME","OZONE","QA_CODE","UPDATE_DATE"
#"KIC003","01/01/2016 00:00:00","","3","01/01/2016 02:33:28"
