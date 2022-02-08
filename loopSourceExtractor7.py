#!/usr/bin/env python3
#
# conda activate sep
#	for the correct environment
#


from pathlib import Path
import ccdproc as ccdp
import numpy as np
from astropy import units as u
from astropy.io import fits
import sep
# import matplotlib.pyplot as plt
from matplotlib import rcParams

filt = "."

#kernel = np.array([[1., 2., 3., 2., 1.],
#				   [2., 3., 5., 3., 2.],
#				   [3., 5., 8., 5., 3.],
#				   [2., 3., 5., 3., 2.],
#				   [1., 2., 3., 2., 1.]])

kernel = np.array([[1., 2.,  3.,  2., 2., 1.],
				   [2., 3., 10., 10., 2., 2.],
				   [3., 5., 19., 19., 5., 3.],
				   [2., 5., 19., 19., 5., 2.],
				   [2., 3., 10., 10., 2., 2.],
				   [1., 2.,  3.,  2., 2., 1.]])

#kernel = np.array([[0.84, 1.13, 1.36, 1.51, 1.56, 1.51, 1.36, 1.13, 0.84 ],
#				   [1.13, 1.46, 1.74, 1.93, 2.00, 1.93, 1.74, 1.46, 1.13 ],
#				   [1.36, 1.74, 2.07, 2.33, 2.43, 2.33, 2.07, 1.74, 1.36 ],
#				   [1.51, 1.93, 2.33, 2.69, 2.87, 2.69, 2.33, 1.93, 1.51 ],
#				   [1.56, 2.00, 2.43, 2.87, 3.30, 2.87, 2.43, 2.00, 1.56 ],
#				   [1.51, 1.93, 2.33, 2.69, 2.87, 2.69, 2.33, 1.93, 1.51 ],
#				   [1.36, 1.74, 2.07, 2.33, 2.43, 2.33, 2.07, 1.74, 1.36 ],
#				   [1.13, 1.46, 1.74, 1.93, 2.00, 1.93, 1.74, 1.46, 1.13 ],
#				   [0.84, 1.13, 1.36, 1.51, 1.56, 1.51, 1.36, 1.13, 0.84 ]])

print("Photometry for science frames in ", filt)

scienceFiles = ccdp.ImageFileCollection(filt)
scienceImages = scienceFiles.files_filtered(imagetyp='Light Frame', include_path=False)

filterPath = Path(filt)

print("%-64s"%"Filename", "%-6s"%"Armss", "%-6s"%"Exptm", "%-11s"%"Flux", "%-7s"%"Fluxerr", "%-5s"%"SNR", "%-3s"%"num", "%-3s"%"Flg", "%-6s"%"Xcoord", "%-6s"%"Ycoord", "%-5s"%"ObRad", "%-6s"%"MaxPix", "%-6s"%"Bkgnd")

central_zoom = 512
xsize = 2048
ysize = 2048
cameraGain = 2.19
print("chip x / y / zoom / gain:",xsize,"/",ysize,"/",central_zoom,"/",cameraGain)

xindex = int(xsize/2)
yindex = int(ysize/2)

print(xindex,yindex)

x1 = int(xsize/2 - central_zoom/2)
x2 = int(xsize/2 + central_zoom/2)
y1 = int(ysize/2 - central_zoom/2)
y2 = int(ysize/2 + central_zoom/2)


for file_name in scienceImages:

#	print("Processing in",filterPath,":", file_name)
#	imageFile = ccdp.CCDData.read(filterPath / file_name, unit=u.adu)
	imageFile = ccdp.CCDData(fits.getdata(filterPath / file_name), meta=fits.getheader(filterPath / file_name), unit=u.adu)

	imageHeader = imageFile[0].header
#	imageData   = imageFile.data.astype(float)
	imageData   = imageFile.data[y1:y2,x1:x2].astype(float)
#	print(imageData)
	
	airmass = imageHeader['AIRMASS']
	exptime = imageHeader['EXPTIME']
	
	bkg = sep.Background(imageData)
	bkgLevel = bkg.globalback
	#print(bkg.globalrms*17.5)
	
	#imageObjects = sep.extract(imageData, bkg.globalrms*17.5, err=bkg.globalrms, filter_kernel=kernel)
	imageObjects = sep.extract(imageData, bkgLevel+bkg.globalrms*4, filter_kernel=kernel)
#	print(imageObjects)
#	print(len(imageObjects))
	
	apertureRadius = 15.0
	bk_inner_Radius = apertureRadius + 10.0
	bk_outer_Radius = apertureRadius + 15.0
	
	
	flux, fluxerr, flag = sep.sum_circle(imageData, imageObjects['x'], imageObjects['y'],
								     apertureRadius, err=bkg.globalrms, gain=cameraGain,
									 bkgann=(bk_inner_Radius,bk_outer_Radius))
	objectRadius, flag = sep.flux_radius(imageData, imageObjects['x'], imageObjects['y'],6.*imageObjects['a'], 0.5,
						  normflux=flux, subpix=5)
	flux, fluxerr, flag = sep.sum_circle(imageData, imageObjects['x'], imageObjects['y'],
								     objectRadius*2, err=bkg.globalrms, gain=cameraGain,
									 bkgann=(objectRadius*2 + 10, objectRadius*2 + 15))
#	print(objectRadius)
	
	ab = np.array([flux, fluxerr, flag, imageObjects['x'], imageObjects['y'], objectRadius])
	abIndexList = np.argsort(ab)
	# print(len(abIndexList[0]))
	if len(abIndexList[0]) > 0:
    #	print(abIndexList)
		indexab = abIndexList[0,-1]
    #	print(indexab)
    #	print(ab)
		xadjusted = (xsize - central_zoom) / 2 + ab[3,indexab]
		yadjusted = (ysize - central_zoom) / 2 + ab[4,indexab]
		
		# look for spot saturation by determining the max value of the pixels
		spotSize = 16
		x_lower = int(xadjusted - spotSize)
		x_upper = int(xadjusted + spotSize)
		y_lower = int(yadjusted - spotSize)
		y_upper = int(yadjusted + spotSize)
		imageSubData   = imageFile.data[y_lower:y_upper,x_lower:x_upper].astype(int)
		nx, ny = imageSubData.shape
		imageSubDatah = np.reshape(imageSubData, nx*ny)      # change the shape to be 1d
		s = np.sort(imageSubDatah)
		maxPixelVal = s[-1]
		
		print("%-64s"%file_name, "%6.3f"%airmass, "%6.2f"%exptime, "%11.1f"%ab[0,indexab], "%7.1f"%ab[1,indexab], "%5.0f"%(ab[0,indexab]/ab[1,indexab]), "%3d"%len(imageObjects), "%3d"%ab[2,indexab], "%6.1f"%xadjusted, "%6.1f"%yadjusted, "%5.2f"%ab[5,indexab], "%6d"%maxPixelVal, "%5.1f"%bkgLevel)
	else:
		print("%-64s"%file_name, "%6.3f"%airmass, "%6.2f"%exptime, "  NoDet")
