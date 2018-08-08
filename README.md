CASTNet Evaluation
------------------

Each subfolder has its own Makefile and README.md. This README.md describes
the overall process.


Directory Structure
-------------------
./
 |- README.md
 |- LICENSE
 |- Makefile
 |- input/
 |- obs/
 |- mod/
 |- figs/


Quick Start
-----------
Edit Makefile to change the year and root for CONC files. Then type run
make (i.e., `make`).


Steps
-----
  1. Get input data (`make -C input`)
  2. Make a netCDF file of CASTNet obs (`make -C obs`)
  3. Make a netCDF file of Model at CASTNet obs locations (`make -C mod`)
  4. Make figures (`make -C figs`)

