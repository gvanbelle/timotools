#!/usr/bin/env python3
#
# readNoiseEst2.py
#
# Usage:
#  readNoiseEst2.py 'filename*.fits'
#  (quotes are important)


from numpy import *
from astropy.io import fits
import sys
import itertools
import glob

#path = ("./")
print("#file1","file2","min","max","mean","median","stdev")


#for files in itertools.combinations(glob.glob(path + sys.argv[1]), 2):
for files in itertools.combinations(glob.glob(sys.argv[1]), 2):
	file1, file2 = map(open, files)
	#print(file1.name,file2.name)  
    
	# read in the files
	# change the file names as appropriate
	h1 = fits.open(file1.name)
	h2 = fits.open(file2.name)

	# copy the image data into a numpy (numerical python) array
	img1 = h1[0].data
	img2 = h2[0].data

	# find the difference in the images
	diff = img2.astype(float32)-img1.astype(float32)

	#img is a 2-d array, need to change to 1-d to make a histogram
	#imgh = 1.0*img # make a copy
	nx, ny = diff.shape # find the size of the array
	imgh = reshape(diff, nx*ny) # change the shape to be 1d

	f = 0.0001 # ignore first and last fraction f of points
	s = sort(imgh)
	  
	f_index=int(f*len(s))
	vmin = s[f_index]
	f_index=int((1-f)*len(s))
	vmax = s[f_index]

	q = where((imgh >= vmin) & (imgh <= vmax))
	imghcut = imgh[q]

	print(file1.name, file2.name, min(imghcut), max(imghcut), mean(imghcut), median(imghcut), std(imghcut))


