YYYY=2016
MOD=$(wildcard ../mod/*_$(YYYY).nc )
OBS=$(wildcard ../obs/*$(YYYY).nc )

all: ts/updated hist2d/updated

ts/updated: ts.py $(OBS) $(MOD)
	python $^ --modname CMAQ --obsname CASTNET

hist2d/updated: hist2d.py $(OBS) $(MOD)
	python $^ --modname CMAQ --obsname CASTNET

