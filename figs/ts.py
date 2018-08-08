from PseudoNetCDF import pncopen
import numpy as np
import matplotlib.pyplot as plt
from warnings import warn
from scipy.stats import pearsonr, spearmanr
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--seasonkeys', default = 'ALL DJF MAM JJA SON'.split(), type = lambda x: x.split(','), help = 'comma delimited seasons (ALL,DJF,MAM,SON)')
parser.add_argument('--obsname', default = 'OBS')
parser.add_argument('--modname', default = 'MOD')
parser.add_argument('obspath')
parser.add_argument('modpath')
args = parser.parse_args()

cmaqf = pncopen(args.modpath, addcf = False, format = 'netcdf')
cnetf = pncopen(args.obspath, addcf = False, format = 'netcdf')

times = cmaqf.getTimes()
season = dict(JULY = [7],
              DJF = [12, 1, 2],
              MAM = [3, 4, 5],
              JJA = [6, 7, 8],
              SON = [9, 10, 11],
              ALL = range(1, 13))

season = dict([(seasonk, season[seasonk]) for seasonk in args.seasonkeys])

sitenames = cnetf.SITENAMES.split('|')
for monthk, monthi in season.items():
    tslice = np.array([t.month in monthi for t in times])
    tcmaqf = cmaqf.sliceDimensions(time = tslice).removeSingleton()
    tcnetf = cnetf.sliceDimensions(time = tslice)
    for si in range(len(cmaqf.dimensions['site'])):
        sitename = sitenames[si]
        scmaqf = tcmaqf.sliceDimensions(site = si)
        scnetf = tcnetf.sliceDimensions(site = si)
        cnetO3 = np.ma.masked_values(scnetf.variables['O3'][:], -999.)
        cmaqO3 = scmaqf.variables['O3'][:]
        cmaqO3m = np.ma.masked_where(cnetO3.mask, cmaqO3)
        if cnetO3.mask.all():
            warn('Skip ' + sitename + '; no data')
            continue
        x1 = tcnetf.getTimes()
        x2 = tcmaqf.getTimes()
        print(sitename, x1.min(), x1.max())
        y1 = cnetO3[:].ravel()
        y2 = cmaqO3[:].ravel()
        y1c = y1.compressed()
        y2c = cmaqO3m[:].ravel().compressed()
        cmin = 1
        o3max = np.max([y1.max(), y2.max()]) // 5 * 5 + 5
        bins = np.arange(0, o3max + 2.5, 2.5)
        plt.close()
        cnetts = plt.plot(x1, y1, label = 'CNET', color = 'k', linestyle = 'none', marker = 'o')
        ax = cnetts[0].axes
        cmaqts = ax.plot(x2, y2, label = 'CMAQ', color = 'blue', linestyle  = '-')
        #ax.set_xlim(x[0], x[-1])
        pr = pearsonr(y1, y2)
        sr = spearmanr(y1c, y2c)
        ax.set_title('Pearson (r={:0.2f}, p={:0.2f}); Spearman (r={:0.2f}, p={:0.2f})'.format(*(pr + sr)))
        ax.set_ylabel('CMAQ (blue), CASTNet (black) O3 ppb')
        ax.legend()
        if monthk == 'ALL':
            xdl = plt.matplotlib.dates.AutoDateLocator(maxticks = 24)
        else:
            xdl = plt.matplotlib.dates.DayLocator([1, 8, 15, 22])
        ax.xaxis.set_major_locator(xdl)
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
        ax.set_position([.1, .2, .8, .7])
        plt.setp(ax.get_xticklabels(), rotation = 90)
        ax.figure.savefig('figs/ts/ts_{}_{}.png'.format(sitename, monthk))

import os
os.system('date > figs/ts/updated')
