import PseudoNetCDF as pnc
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('obspath')
parser.add_argument('modpath')
args = parser.parse_args([
    '../obs/CASTNET2016.nc',
    '../mod/combine_aconc_v521_intel17.0_HEMIS_cb6_2016.nc',
])

plt.rcParams['axes.labelsize'] = 18
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
modf = pnc.pncopen(args.modpath).copy()
obsf = pnc.pncopen(args.obspath).copy()

lat = obsf.variables['latitude']
lon = obsf.variables['longitude']
tzoff = -obsf.variables['TIME_OFFSET'][:].astype('i')

tidx = np.arange(24, len(modf.dimensions['time']) - 24)[:, None] + tzoff
sidx = np.arange(len(obsf.dimensions['site']))[None,  :].repeat(tidx.shape[0], 0)

times = obsf.getTimes()

oto3 = obsf.variables['O3'][tidx, sidx].T
mto3 = modf.variables['O3'][tidx, 0, sidx].T
bto3 = mto3 - oto3


vals = bto3.reshape(-1, 24).T
hidx, sidx = np.indices(vals.shape)
y = vals.ravel()
x = np.ma.masked_where(
    y.mask,
    hidx.ravel()
).compressed()
y = y.compressed()

dbins = np.arange(25), np.arange(-62.5, 67.5, 5)
ax = plt.axes([.15, .15, .7, .8])
cax = plt.axes([.86, .15, .025, .8])
(counts, xedges, yedges, p) = ax.hist2d(x, y, normed=False, cmap='jet', bins=dbins, cmin=1)
ax.figure.colorbar(p, cax=cax)
ax.set_xticks(np.arange(0, 25, 4))
ax.set_ylabel('bias (ppb)')
ax.set_xlabel('hour of day')
ax.figure.savefig('diurnal/diurnal_bias.png');
ax.cla()
cax.cla()

obins = np.arange(25), np.arange(0, 85, 5)
y = oto3.reshape(-1, 24).T.ravel().compressed()
(counts, xedges, yedges, p) = ax.hist2d(x, y, normed=False, cmap='jet', bins=obins, cmin=1)
ax.figure.colorbar(p, cax=cax)
ax.set_xticks(np.arange(0, 25, 4))
ax.set_ylabel('obs (ppb)')
ax.set_xlabel('hour of day')
ax.figure.savefig('diurnal/diurnal_obs.png');

obins = np.arange(25), np.arange(0, 85, 5)
y = np.ma.masked_where(oto3.mask, mto3).reshape(-1, 24).T.ravel().compressed()
(counts, xedges, yedges, p) = ax.hist2d(x, y, normed=False, cmap='jet', bins=obins, cmin=1)
ax.figure.colorbar(p, cax=cax)
ax.set_xticks(np.arange(0, 25, 4))
ax.set_ylabel('model (ppb)')
ax.set_xlabel('hour of day')
ax.figure.savefig('diurnal/diurnal_mod.png');

tint = OrderedDict()
for ti in [1, 8, 15, 22]:
    tint['%02d' % ti] = [ti]

tint['09to15'] = list(range(9, 16))
tint['11to17'] = list(range(11, 18))
tint['00to05'] = list(range(0, 6))

for tk, tis in tint.items():
    plt.close();
    ax = plt.axes([.15, .2, .7, .75])
    cax = plt.axes([.86, .2, .025, .75])
    vals = bto3.reshape(bto3.shape[0], -1, 24)[:,:,tis].mean(2).T
    bins = np.arange(1, vals.shape[0] + 1), np.arange(-62.5, 67.5, 5)
    didx, sidx = np.indices(vals.shape)
    jday = didx + 2
    y = vals.ravel()
    x = np.ma.masked_where(
        y.mask,
        jday.ravel()
    ).compressed()
    y = y.compressed()
    print(tk, y.size)
    (counts, xedges, yedges, p) = ax.hist2d(x, y, normed=False, cmap='jet', bins=bins, cmin=1)
    ax.figure.colorbar(p, cax=cax)
    ax.set_xticks(np.arange(1, 366, 30))
    plt.setp(ax.xaxis.get_ticklabels(), rotation=90)
    ax.set_ylabel('%s LST bias (ppb)' % tk)
    ax.set_xlabel('day of year')
    ax.figure.savefig('diurnal/annual_%s.png' % tk)
