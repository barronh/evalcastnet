TARGETS=$(notdir $(sort $(wildcard $(CONCROOT)/combine_*)))

all: combine_aconc_v521_intel17.0_HEMIS_cb6_$(YYYY).nc

combine_aconc_v521_intel17.0_HEMIS_cb6_$(YYYY).nc: $(TARGETS)
	python extract.py $^ $@

combine_aconc_v521_intel17.0_HEMIS_cb6_%: $(CONCROOT)/combine_aconc_v521_intel17.0_HEMIS_cb6_% ../obs/CASTNET$(YYYY).nc
	pncgen -O -f ioapi -s LAY,0 --rename d,points,site -- -v O3 --extractmethod=ll2ij --extract-file=../obs/CASTNET$(YYYY).nc $< $@

	
