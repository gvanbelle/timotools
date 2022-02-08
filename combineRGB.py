#import pyfits
from astropy.io import fits
import numpy as np
from matplotlib import pyplot as plt
#import pylab as py
import img_scale
 
hdu3 = fits.open('20210407_040524-M 67-3-Johnson-R-060.fts')
hdu2 = fits.open('20210407_040910-M 67-3-Johnson-V-060.fts')
hdul = fits.open('20210407_041257-M 67-3-Johnson-B-060.fts')

j_img = hdul[0].data
h_img = hdu2[0].data
k_img = hdu3[0].data

img = np.zeros((j_img.shape[0], j_img.shape[1], 3), dtype=float)
img[:,:,0] = img_scale.linear(k_img, scale_min=0, scale_max=10000)
img[:,:,1] = img_scale.linear(h_img, scale_min=0, scale_max=10000)
img[:,:,2] = img_scale.linear(j_img, scale_min=0, scale_max=10000)

plt.clf()
plt.figure(figsize = (20.48,20.48))
plt.imshow(img, aspect='equal')
plt.title('Blue = B, Green = V, Red = R')
plt.savefig('my_rgb_image.png')