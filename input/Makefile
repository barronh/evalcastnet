all: ozone_$(YYYY).csv site.csv

ozone_$(YYYY).csv: ozone_$(YYYY).zip
	unzip $< $@

site.csv: site.zip
	unzip $< $@

ozone_$(YYYY).zip:
	wget ftp://ftp.epa.gov/castnet/data/ozone_$(YYYY).zip

site.zip:
	wget ftp://ftp.epa.gov/castnet/data/site.zip
