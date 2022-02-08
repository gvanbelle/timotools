import numpy as np
from photutils import datasets
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


arg = glob('*.fits.gz',recursive=True)
total = len(arg)

for i,filename in enumerate(arg):

	print("Examining ",i+1," of ",total," : ",filename)
    
	data=fits.open(filename)
	header=data[0].header
	scidata=data[0].data[800:1200,800:1200].astype(float)

	airmass = header['AIRMASS']

	scidata -= np.median(scidata)

	bkg_sigma = mad_std(scidata)  
	daofind = DAOStarFinder(fwhm=4., threshold=3.*bkg_sigma)  
	sources = daofind(scidata)  
#	for col in sources.colnames:  
#		sources[col].info.format = '%.8g'  # for consistent table output
#	print(sources)  

	positions = np.transpose((sources['xcentroid'], sources['ycentroid']))  
	apertures = CircularAperture(positions, r=30.)  
	phot_table = aperture_photometry(scidata, apertures)  
	for col in phot_table.colnames:  
		phot_table[col].info.format = '%.8g'  # for consistent table output
#	print(phot_table)  

	row=sort_table(phot_table, 3)
	print(airmass,row[-1][3],row[-1][1],row[-1][2])
	
#	for row in sort_table(phot_table, 3):
#		print(row)
