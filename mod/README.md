mod
---

Make NetCDF file that matches ../obs/CASTNETYYYY.nc

Quick Start
-----------

Run make with CONCROOT and YYYY specified.

```
CONCROOT=/path/to/conc/ YYYY=2016 make
```

Directory Structure
-------------------
./
 |- extract.py
 |- Makefile

Prerequisites
-------------
1. ../obs/CASTNETYYY.nc
2. $(CONCROOT)/*$(YYYY)*

