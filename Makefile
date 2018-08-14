CONCROOT=/work/ROMO/global/CMAQv5.2.1/2016fe_hemi_cb6_16jh/108km/basecase/extr
YYYY=2016

export YYYY
export CONCROOT

all:
	make -C input
	make -C obs
	make -C mod
	make -C figs



mod/combine_aconc_v521_intel17.0_HEMIS_cb6_%: $(CONCROOT)/combine_aconc_v521_intel17.0_HEMIS_cb6_%
	pncgen -O -f ioapi -s LAY,0 --rename d,points,site -- -v O3 --extractmethod=ll2ij --extract-file=CASTNET$(YYYY).nc $< $@

obs/CASTNET$(YYYY).nc:
	python csv2nc.py 

copy:
	
