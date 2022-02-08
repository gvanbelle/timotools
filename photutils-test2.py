#!/usr/bin/env python3
#

import numpy as np
from photutils import datasets
from photutils import DAOStarFinder
from astropy.stats import mad_std
from astropy.io import fits
from astropy.nddata.utils import Cutout2D
import matplotlib.pyplot as plt
from astropy import wcs
import numpy as np
import os
from glob import glob
from photutils import aperture_photometry, CircularAperture
import operator

def sort_table(table, col=0):
	return sorted(table, key=operator.itemgetter(col))


arg = glob('*.fits',recursive=True)
total = len(arg)

print("#num :","filename","airmass","exptime","flux","x0","y0")

for i,filename in enumerate(arg):

#	print("Examining ",i+1," of ",total," : ",filename)
    
	data=fits.open(filename)
	header=data[0].header
	scidata=data[0].data.astype(float) #[1500:1700,950:1150].astype(float)

	airmass = header['AIRMASS']
	exptime = header['EXPTIME']

	scidata -= np.median(scidata)

	bkg_sigma = mad_std(scidata)  
	daofind = DAOStarFinder(fwhm=10., threshold=2.*bkg_sigma)  
	sources = daofind(scidata)  
#	for col in sources.colnames:  
#		sources[col].info.format = '%.8g'  # for consistent table output
#	print(sources)  

	positions = np.transpose((sources['xcentroid'], sources['ycentroid']))  
	apertures = CircularAperture(positions, r=10.)  
	phot_table = aperture_photometry(scidata, apertures)  
	for col in phot_table.colnames:  
		phot_table[col].info.format = '%.8g'  # for consistent table output
	print(phot_table)  

	row=sort_table(phot_table, 3)
#	print(row)
	print("%3d"%(i+1),"of",total,":",filename,"%5.2f"%airmass,"%5.2f"%exptime,"%10.2f"%row[-1][3],row[-1][1],row[-1][2])
#	print(i+1,"of",total,":",filename,"%5.2f"%airmass,"%5.2f"%exptime,
#			"%10.2f"%row[-1][3],"%7.2f"%row[-1][1],"%7.2f"%row[-1][2])
	
#	for row in sort_table(phot_table, 3):
#		print(row)
