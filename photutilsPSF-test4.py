#!/usr/bin/env python3
#

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
from photutils import aperture_photometry, CircularAperture, MedianBackground
import operator
from photutils.detection import IRAFStarFinder
from photutils.psf import IntegratedGaussianPRF, DAOGroup
from photutils.background import MMMBackground, MADStdBackgroundRMS
from astropy.modeling.fitting import LevMarLSQFitter
from astropy.stats import gaussian_sigma_to_fwhm
from astropy.stats import SigmaClip
from photutils.psf import IterativelySubtractedPSFPhotometry
import warnings

def sort_table(table, col=0):
	return sorted(table, key=operator.itemgetter(col))


arg = glob('*.fits',recursive=True)
total = len(arg)
sigma_psf = 2

print("#num :","filename","HA","exptime","flux_0","x0","y0","flux_fit","flux_unc")
warnings.filterwarnings("ignore")

for i,filename in enumerate(arg):

	#print(i+1,"of",total,":",filename)
	
	data=fits.open(filename)
	header=data[0].header
#	scidata=data[0].data.astype(float)
	scidata=data[0].data[500:1500,1000:2000].astype(float)

	airmass = header['AIRMASS']
	exptime = header['EXPTIME']


	bkgrms = MADStdBackgroundRMS()
	std = bkgrms(scidata)
	iraffind = IRAFStarFinder(threshold=3.5*std,
							fwhm=sigma_psf*gaussian_sigma_to_fwhm,
							#minsep_fwhm=0.01, roundhi=5.0, roundlo=-5.0,
							#sharplo=0.0, sharphi=2.0
                            )
	daogroup = DAOGroup(2.0*sigma_psf*gaussian_sigma_to_fwhm)
    
#	bkg_sigma = mad_std(scidata)  
#	daofind = DAOStarFinder(fwhm=10., threshold=2.*bkg_sigma)  

#	mmm_bkg = MMMBackground()
	sigma_clip = SigmaClip(sigma=3.0)
	mmm_bkg = MedianBackground(sigma_clip)
    
	fitter = LevMarLSQFitter()
	psf_model = IntegratedGaussianPRF(sigma=sigma_psf)
	photometry = IterativelySubtractedPSFPhotometry(finder=iraffind, #daofind,
													group_maker=daogroup,
													bkg_estimator=mmm_bkg,
													psf_model=psf_model,
													fitter=LevMarLSQFitter(),
													niters=3, fitshape=(21,21))
	result_table = photometry(image=scidata)
	residual_image = photometry.get_residual_image()

#	print(result_table)

	for col in result_table.colnames:  
		result_table[col].info.format = '%.8g'  # for consistent table output
	print(result_table)  

	row=sort_table(result_table, 4)
	print("%3d"%(i+1),"of",total,":",filename,"%5.2f"%airmass,"%5.2f"%exptime,"%10.2f"%row[-1][4],"%7.2f"%row[-1][0],
            "%7.2f"%row[-1][2],"%10.2f"%row[-1][5],"%10.2f"%row[-1][8])
	
#	for row in sort_table(result_table, 3):
#		print(row)
