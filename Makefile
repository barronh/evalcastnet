CONCROOT=/work/ROMO/global/CMAQv5.2.1/2016fe_hemi_cb6_16jh/108km/basecase/extr
YYYY=2016

export YYYY
export CONCROOT

all:
	$(MAKE) -C input
	$(MAKE) -C obs
	$(MAKE) -C mod
	$(MAKE) -C figs
