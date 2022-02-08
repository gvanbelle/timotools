#!/usr/bin/env python3
#
#################################################################################
# Python script using astropy to identify all unique OBJECT files in a          #
# directory and sort them into OBJECT unique subdirectories                     #
# source: Gerard van Belle Feb 2022                                             #
#################################################################################
#
# Usage: cd to the data directory, then execute the code:
#       $ sortAsteroids.py
#

from astropy.io import fits
import numpy as np
import os
from glob import glob

# function to get unique values
def unique(list1):
    x = np.array(list1)
    return np.unique(x)

arg = glob('*.fits',recursive=True)

totalFiles = len(arg)

print("Number of FITS files found: ",totalFiles)
print(arg)

targets = []

for i,filename in enumerate(arg):
    print("Reading ",i+1," of ",totalFiles," : ",filename)
    hdul = fits.open(filename)
    targets.append(hdul[0].header['OBJECT'])
    print(targets[i])
    hdul.close()

#print(targets)
uniqueTargets = unique(targets)
totalTargets = len(uniqueTargets)
print("Number of unique targets: ", totalTargets)
print(uniqueTargets)
#dirList = []
#for s in unique(targets):
#    dirList.append('MP' + s)
#print(dirList)

for i,directoryName in enumerate(uniqueTargets):
    print("Making directory ",i+1," of ",totalTargets," : ",directoryName)
    isExist = os.path.exists(directoryName)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(directoryName)

for i,filename in enumerate(arg):
    hdul = fits.open(filename)
    targetPath = hdul[0].header['OBJECT']
    print("Moving",i+1,"of",totalFiles,":",filename, "to", targetPath)
    os.rename(filename, os.path.join(targetPath, filename))

