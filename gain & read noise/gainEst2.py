#!/usr/bin/env python3
#
# readNoiseEst2.py
#
# Usage:
#  gainEst2.py 'filename*.fits'
#  (quotes are important)


from numpy import *
from astropy.io import fits
import sys
import itertools
import glob

#path = ("./")
print("#file1","file2","min","max","mean","median","stdev")

avg_DB=[0]
stdev_DB=[0]

#for files in itertools.combinations(glob.glob(path + sys.argv[1]), 2):
for files in itertools.combinations(glob.glob(sys.argv[1]), 2):
	file1, file2 = map(open, files)
	#print(file1.name,file2.name)  
    
	# read in the files
	# change the file names as appropriate
	h1 = fits.open(file1.name)
	h2 = fits.open(file2.name)

	size = int(sys.argv[2])
	centerX = int(3072/2)
	centerY = int(2048/2)
	X1 = int(centerX - size/2)
	X2 = int(centerX + size/2)
	Y1 = int(centerY - size/2)
	Y2 = int(centerY + size/2)

	# copy the image data into a numpy (numerical python) array
	img1 = h1[0].data[X1:X2,Y1:Y2]
	img2 = h2[0].data[X1:X2,Y1:Y2]

	# find the difference in the images
	img12sum = img2.astype(float32)+img1.astype(float32)
	img12diff = img2.astype(float32)-img1.astype(float32)

	#img12diff is a 2-d array, need to change to 1-d to make a histogram
    
	nx, ny = img12sum.shape                    # find the size of the array
	img12sumh = reshape(img12sum, nx*ny)      # change the shape to be 1d
	f = 0.001                                   # ignore first and last fraction f of points
	s = sort(img12sumh)
	f_index=int(f*len(s))
	vmin = s[f_index]
	f_index=int((1-f)*len(s))
	vmax = s[f_index]
	q = where((img12sumh >= vmin) & (img12sumh <= vmax))
	img12sumhcut = img12sumh[q]

	nx, ny = img12diff.shape                    # find the size of the array
	img12diffh = reshape(img12diff, nx*ny)      # change the shape to be 1d
	f = 0.001                                   # ignore first and last fraction f of points
	s = sort(img12diffh)
	f_index=int(f*len(s))
	vmin = s[f_index]
	f_index=int((1-f)*len(s))
	vmax = s[f_index]
	q = where((img12diffh >= vmin) & (img12diffh <= vmax))
	img12diffhcut = img12diffh[q]

	print(file1.name, file2.name, mean(img12sumhcut)/2, var(img12diffhcut)/2)
	
	stdev_DB.append(var(img12diffhcut)/2)
	avg_DB.append(mean(img12sumhcut)/2)

stdev_DB.pop(0)
avg_DB.pop(0)
print(sys.argv[1],mean(avg_DB),"+-",std(avg_DB)," ADUs ",mean(stdev_DB),"+-",std(stdev_DB)," ADUs")


