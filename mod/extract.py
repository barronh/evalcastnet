import PseudoNetCDF as pnc
from glob import glob
import numpy as np
import sys

paths = sys.argv[1:]
inpaths = paths[:-1]
outpath = paths[-1]

def openfile(path):
    """
    Clean out duplicated days
    """
    mo = int(path[-2:])
    f = pnc.pncopen(path, format='netcdf').subsetVariables(['O3'])
    times = f.getTimes()
    tidx = np.array([ti for ti, t in enumerate(times) if t.month == mo])
    return f.sliceDimensions(TSTEP=tidx)

    
outf = pnc.sci_var.stack_files([openfile(path) for path in inpaths], 'TSTEP')
try:
    pnc.conventions.ioapi.add_cf_from_ioapi(outf)
except Exception:
    pass
outf = outf.renameDimensions(TSTEP='time')
outf.save(outpath, format='NETCDF4_CLASSIC')
