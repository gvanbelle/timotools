#################################################################################
#Python script using astropy to load and crop  a certain portion of a FITS image#
# while preserving the WCS                                                      #
# source: Behnam Javanmardi Dec 2017                                            #
#################################################################################

from astropy.io import fits
from astropy.nddata.utils import Cutout2D
import matplotlib.pyplot as plt
from astropy import wcs
import numpy as np
import os
from glob import glob

size = 2048
x_cen = 1536
y_cen = 1024

arg = glob('*/*.fits',recursive=True)

total = len(arg)

for i,filename in enumerate(arg):

    print("Cropping ",i+1," of ",total," : ",filename)
    
    data=fits.open(filename)
    header=data[0].header
    scidata=data[0].data

    cropped=Cutout2D(scidata, (x_cen,y_cen), size=size)
    hdu=fits.PrimaryHDU(data=cropped.data, header=header)
    stat = os.stat(filename)                        # get the modification time of the orignal 
    name=os.path.splitext(os.path.splitext(filename)[0])[0]+'_crop.fits'
    hdu.writeto(name, overwrite=True)
    os.utime(name,(stat.st_mtime,stat.st_mtime))    # set the original timestamp to the new file
    os.remove(filename)


