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
#from photutils import aperture_photometry, CircularAperture, CircularAnnulus
import photutils
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
#	scidata=data[0].data.astype(float)
	scidata=data[0].data[500:1500,1000:2000].astype(float)

	airmass = header['AIRMASS']
	exptime = header['EXPTIME']

	threshold = 5
	fwhm = 10

	background = mad_std(scidata)
	daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold*background)  
	sources = daofind(scidata)  

#	for col in sources.colnames:  
#		sources[col].info.format = '%.8g'  # for consistent table output
#	print(sources)  

	positions = np.transpose((sources['xcentroid'], sources['ycentroid']))  

	aperture_radius = 15
	aperture_area = np.pi * aperture_radius**2
	annulus_radius = aperture_radius+2
	annulus_area = np.pi * (annulus_radius**2 - aperture_radius**2)

	apertures = photutils.CircularAperture(positions, r = aperture_radius)
	annulus_apertures = photutils.CircularAnnulus(positions, aperture_radius, annulus_radius)
	
	phot_table = photutils.aperture_photometry(scidata, apertures)
	bkgd_table = photutils.aperture_photometry(scidata, annulus_apertures)
    
	print(phot_table)
	print(bkgd_table)
    
	for tt in phot_table:
		print(phot_table[tt].info)
		#print(phot_table[rows][3])
		phot_table[rows:3] = phot_table[rows:3] - bkgd_table[rows:3] * aperture_area / annulus_area
	
	for col in corr_table.colnames:  
		corr_table[col].info.format = '%.8g'  # for consistent table output
#	print(corr_table)  

	row=sort_table(corr_table, 3)
#	print(row)
	print("%3d"%(i+1),"of",total,":",filename,"%5.2f"%airmass,"%5.2f"%exptime,"%10.2f"%row[-1][3],row[-1][1],row[-1][2])
#	print(i+1,"of",total,":",filename,"%5.2f"%airmass,"%5.2f"%exptime,
#			"%10.2f"%row[-1][3],"%7.2f"%row[-1][1],"%7.2f"%row[-1][2])
	
#	for row in sort_table(phot_table, 3):
#		print(row)
