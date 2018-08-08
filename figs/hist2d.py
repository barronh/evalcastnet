from PseudoNetCDF import pncopen
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--obsname', default = 'OBS')
parser.add_argument('--modname', default = 'MOD')
parser.add_argument('obspath')
parser.add_argument('modpath')
args = parser.parse_args()

cmaqf = pncopen(args.modpath, addcf = False, format = 'netcdf')
cnetf = pncopen(args.obspath, addcf = False, format = 'netcdf')
times = cmaqf.getTimes()
season = dict(DJF = [12, 1, 2],
              MAM = [3, 4, 5],
              JJA = [6, 7, 8],
              SON = [9, 10, 11],
              ALL = list(range(1, 13)))
for monthk, monthi in season.items():
    tslice = np.array([t.month in monthi for t in times])
    print(monthk, monthi, tslice.sum())
    scmaqf = cmaqf.sliceDimensions(time = tslice).removeSingleton()
    scnetf = cnetf.sliceDimensions(time = tslice)
    cnetO3 = np.ma.masked_values(scnetf.variables['O3'][:], -999.)
    cmaqO3 = np.ma.masked_where(cnetO3.mask, scmaqf.variables['O3'][:])
    x = cnetO3[:].ravel()
    y = cmaqO3[:].ravel()
    xc = x.compressed()
    yc = y.compressed()
    xsc = np.sort(xc)
    ysc = np.sort(yc)
    cmin = 1
    o3max = np.maximum(x.max(), y.max()) // 5. * 5 + 5
    bins = np.arange(0, o3max + 2.5, 2.5)
    plt.close()
    hout = plt.hist2d(x, y, normed = False, cmin = cmin, bins = bins, cmap='jet')
    ax = hout[-1].axes
    ax.scatter(xsc, ysc, c = 'k', s = 10.)
    cnetmean = float(xc.mean())
    cnetmin = float(xc.min())
    cnetmax = float(xc.max())
    cmaqmean = float(yc.mean())
    cmaqmin = float(yc.min())
    cmaqmax = float(yc.max())
    vmax = max(cnetmax, cmaqmax)
    pr = pearsonr(xc, yc)
    sr = spearmanr(xc, yc)
    ax.set_title('Pearson (r={:0.2f}, p={:0.2f}); Spearman (r={:0.2f}, p={:0.2f})'.format(*(pr + sr)))
    ax.set_xlabel(args.obsname + ' O3 ppb ({:.0f}, {:.0f}, {:.0f})'.format(cnetmin, cnetmean, cnetmax))
    ax.set_ylabel(args.modname + ' O3 ppb ({:.0f}, {:.0f}, {:.0f})'.format(cnetmin, cnetmean, cnetmax))
    ax.plot([0, vmax], [0, vmax], color = 'k')
    ax.figure.savefig('figs/hist2d/hist2d_O3_' + monthk + '.png')

os.system('touch > figs/hist2d/updated')
