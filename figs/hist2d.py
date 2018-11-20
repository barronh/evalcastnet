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

season = dict(DJF = [12, 1, 2],
              MAM = [3, 4, 5],
              JJA = [6, 7, 8],
              SON = [9, 10, 11],
              ALL = list(range(1, 13)))

def plotslice(cmaqf, cnetf, tslice):
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
    bins = np.arange(0, o3max + 5, 5)
    plt.close()
    ax = plt.gca()
    hout = ax.hist2d(x, y, normed=False, cmin=cmin, bins=bins, cmap='jet')
    counts = np.ma.masked_invalid(hout[0])
    ax = hout[-1].axes
    ax.scatter(xsc, ysc, c = 'k', s = 10.)
    cnetmean = float(xc.mean())
    cnetmin = float(xc.min())
    cnetmax = float(xc.max())
    cmaqmean = float(yc.mean())
    cmaqmin = float(yc.min())
    cmaqmax = float(yc.max())
    vmax = max(cnetmax, cmaqmax)
    ax.plot([0, vmax], [0, vmax], color = 'k')
    pr = pearsonr(xc, yc)
    sr = spearmanr(xc, yc)
    ax.set_title('Pearson (r={:0.2f}, p={:0.2f}); Spearman (r={:0.2f}, p={:0.2f})'.format(*(pr + sr)))
    ax.set_xlabel(args.obsname + ' O3 ppb ({:.0f}, {:.0f}, {:.0f})'.format(cnetmin, cnetmean, cnetmax))
    ax.set_ylabel(args.modname + ' O3 ppb ({:.0f}, {:.0f}, {:.0f})'.format(cmaqmin, cmaqmean, cmaqmax))
    return ax.figure


cmaqf = pncopen(args.modpath, addcf = False, format = 'netcdf').copy().removeSingleton()
cnetf = pncopen(args.obspath, addcf = False, format = 'netcdf').copy()
times = cmaqf.getTimes()

for monthk, monthi in season.items():
    tslice = np.array([t.month in monthi for t in times])
    print(monthk, monthi, tslice.sum())
    fig = plotslice(cmaqf, cnetf, tslice)
    fig.savefig('hist2d/hist2d_O3_' + monthk + '.png')

lidx = (np.arange(24, len(times) - 24)[:,None] - cnetf.variables['TIME_OFFSET']).astype('i')
lidx.dimensions = ('time', 'site')
uidx, sidx = np.indices(lidx[:].shape)
sidx = lidx * 0 + sidx
cmaqlf = cmaqf.sliceDimensions(time=slice(48, None))
cmaqlf.variables['O3'][:] = np.nan
cmaqlf.variables['O3'][:] = cmaqf.variables['O3'][lidx, sidx]
cnetlf = cnetf.sliceDimensions(time=slice(48, None))
cnetlf.variables['O3'][:] = np.nan
cnetlf.variables['O3'][:] = cnetf.variables['O3'][lidx, sidx]

plotslice(cmaqlf, cnetlf, tslice=slice(1, None, 24)).savefig('hist2d/hist2d_O3_01LST.png')
plotslice(cmaqlf, cnetlf, tslice=slice(8, None, 24)).savefig('hist2d/hist2d_O3_08LST.png')
plotslice(cmaqlf, cnetlf, tslice=slice(15, None, 24)).savefig('hist2d/hist2d_O3_15LST.png')
plotslice(cmaqlf, cnetlf, tslice=slice(30*24*2+1, 30*24*5+1, 24)).savefig('hist2d/hist2d_O3_01LST_MAM.png')
plotslice(cmaqlf, cnetlf, tslice=slice(30*24*2+8, 30*24*5+8, 24)).savefig('hist2d/hist2d_O3_08LST_MAM.png')
plotslice(cmaqlf, cnetlf, tslice=slice(30*24*2+15, 30*24*5+15, 24)).savefig('hist2d/hist2d_O3_15LST_MAM.png')
plotslice(cmaqlf, cnetlf, tslice=slice(30*24*5+1, 30*24*8+1, 24)).savefig('hist2d/hist2d_O3_01LST_JJA.png')
plotslice(cmaqlf, cnetlf, tslice=slice(30*24*5+8, 30*24*8+8, 24)).savefig('hist2d/hist2d_O3_08LST_JJA.png')
plotslice(cmaqlf, cnetlf, tslice=slice(30*24*5+15, 30*24*8+15, 24)).savefig('hist2d/hist2d_O3_15LST_JJA.png')

os.system('date > hist2d/updated')
