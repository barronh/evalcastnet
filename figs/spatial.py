import PseudoNetCDF as pnc
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse
import scipy.stats.mstats as mstats

parser = argparse.ArgumentParser()
parser.add_argument('obspath')
parser.add_argument('modpath')
args = parser.parse_args()

modpath = '../mod/combine_aconc_v521_intel17.0_HEMIS_cb6_2016.nc'
obspath = '../obs/CASTNET2016.nc'

modf = pnc.pncopen(modpath)
obsf = pnc.pncopen(obspath)

lat = obsf.variables['latitude']
lon = obsf.variables['longitude']
qa = obsf.variables['O3_QA']
mask = qa[:].filled(0) != 3
mO3 = np.ma.masked_where(mask, modf.variables['O3'][:, 0])
oO3 = np.ma.masked_where(mask, obsf.variables['O3'][:])
times = obsf.getTimes()
seasons = OrderedDict()
seasons['ALL'] = list(range(1, 13))
seasons['DJF'] = [12, 1, 2]
seasons['MAM'] = [3, 4, 5]
seasons['JJA'] = [6, 7, 8]
seasons['SON'] = [9, 10, 11]
bedges = np.linspace(-22.5, 22.5, 10)
bnorm = plt.matplotlib.colors.BoundaryNorm(bedges, 256)
redges = np.arange(0, 1.1, .1)
rnorm = plt.matplotlib.colors.BoundaryNorm(redges, 256)
bcmap = 'seismic'
rcmap = 'Reds'
bmap = Basemap(
    llcrnrlat=10, urcrnrlat=60,
    llcrnrlon=-130, urcrnrlon=-60,
    area_thresh=1e4)

fig = plt.figure(figsize=(10,6))
ax = fig.add_axes([.025, .025, .675, .875])
cax = fig.add_axes([0.725, .025, .025, .875])
pax = fig.add_axes([0.85, .025, .1, .875])
bmap.drawcoastlines(ax=ax)
bmap.drawcountries(ax=ax)
bmap.drawstates(ax=ax)
for season, months in seasons.items():
    print(season)
    pax.cla()
    tidx = np.array([ti for ti, t in enumerate(times) if t.month in months])
    tmO3 = mO3[tidx]
    toO3 = oO3[tidx]
    tbO3 = tmO3[:].mean(0) - toO3[:].mean(0)
    rs = np.ma.masked_invalid([mstats.pearsonr(m, o)[0] for m, o in zip(tmO3.T, toO3.T)])
    print(tbO3.min(), tbO3.max())
    s = bmap.scatter(lon, lat, c=tbO3, norm=bnorm, cmap=bcmap, ax=ax, edgecolors='k')
    cbar = plt.colorbar(s, cax=cax, label='ppb')
    hist, edgesdummy = np.histogram(tbO3, bins=bedges)
    pax.plot(hist.repeat(2, 0) / hist.sum() * 100, bedges.repeat(2, 0)[1:-1])
    pax.set_ylim(bedges[0], bedges[-1])
    pax.xaxis.tick_top()
    pax.yaxis.set_major_formatter(plt.NullFormatter())
    pax.set_xlabel('% Sites')
    pax.xaxis.set_label_position('top')
    ax.set_title('CASTNet ' + season)
    plt.savefig('spatial/O3_bias_{}.png'.format(season))
    del ax.collections[-1]
    pax.cla()
    print(rs.shape)
    s = bmap.scatter(lon, lat, c=rs, norm=rnorm, cmap=rcmap, ax=ax, edgecolors='k')
    cbar = plt.colorbar(s, cax=cax, label='ppb')
    hist, edgesdummy = np.histogram(rs.compressed(), bins=redges)
    pax.plot(hist.repeat(2, 0) / hist.sum() * 100, redges.repeat(2, 0)[1:-1])
    plt.savefig('spatial/O3_r_{}.png'.format(season))
    
