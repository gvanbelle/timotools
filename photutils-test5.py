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
import re

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
	scidata=data[0].data[500:1500,500:2500].astype(float)

	airmass = header['AIRMASS']
	exptime = header['EXPTIME']

	threshold = 5
	fwhm = 10

	background = mad_std(scidata)
	daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold*background)  
	sources = daofind(scidata) 

#	print(sources)

#	for col in sources.colnames:  
#		sources[col].info.format = '%.8g'  # for consistent table output
#	print(sources)  

	positions = np.transpose((sources['xcentroid'], sources['ycentroid']))  

	aperture_radius = 20
	annulus_radius_inner = aperture_radius+10
	annulus_radius_outer = aperture_radius+20
    

	apertures = photutils.CircularAperture(positions, r = aperture_radius)
	annulus_apertures = photutils.CircularAnnulus(positions, annulus_radius_inner, annulus_radius_outer)
	
	apers = [apertures, annulus_apertures]

	phot_table = photutils.aperture_photometry(scidata, apers)
    
	bkg_mean = phot_table['aperture_sum_1'] / annulus_apertures.area
	bkg_sum = bkg_mean * apertures.area
	final_sum = phot_table['aperture_sum_0'] - bkg_sum
	phot_table['residual_aperture_sum'] = final_sum

#	print(phot_table)
    
	for col in phot_table.colnames:  
		phot_table[col].info.format = '%.8g'  # for consistent table output
#	print(phot_table)  

	row=sort_table(phot_table, 5)
#	print(row)
	xcoord = row[-1][1]
	xcoordval = xcoord.value
	ycoord = row[-1][2]
	ycoordval = ycoord.value
	print("%3d"%(i+1),"of",total,":",filename,"%6.3f"%airmass,"%5.1f"%exptime,"%10.1f"%row[-1][5],"%6.1f"%xcoordval,"%6.1f"%ycoordval)
#	print(i+1,"of",total,":",filename,"%5.2f"%airmass,"%5.2f"%exptime,
#			"%10.2f"%row[-1][3],"%7.2f"%row[-1][1],"%7.2f"%row[-1][2])
	
#	for row in sort_table(phot_table, 3):
#		print(row)
