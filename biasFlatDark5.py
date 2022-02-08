#!/usr/bin/env python3
#

from pathlib import Path
import os
# from astropy.visualization import hist

import ccdproc as ccdp
# import matplotlib.pyplot as plt
import numpy as np
import shutil
from astropy.stats import mad_std
from astropy.nddata import CCDData
from astropy import units as u

def CCDData_astype(ccd, dtype='float32', uncertainty_dtype=None):
    # see https://github.com/astropy/astropy/issues/9722

    nccd = ccd.copy()
    nccd.data = nccd.data.astype(dtype)

    try:
        if uncertainty_dtype is None:
            uncertainty_dtype = dtype
        nccd.uncertainty.array = nccd.uncertainty.array.astype(
            uncertainty_dtype)
    except AttributeError:
        # If there is no uncertainty attribute in the input ``ccd``
        pass

    return nccd

calibratorsPath = Path('Calibration')
reduced_images = ccdp.ImageFileCollection(calibratorsPath)

calMastersPath = Path('.', 'calMasters')
calMastersPath.mkdir(exist_ok=True)

#
# need to check if 'master_bias.fits' already exists here, and skip 
# creating if so
#

fileCheck = Path(calMastersPath / 'master_bias.fits')
if fileCheck.exists():
    print('master_bias.fits exists, reading.')
    combined_bias = ccdp.CCDData.read(calMastersPath / 'master_bias.fits', unit="adu")
else:
    print("master_bias.fits does not exist, generating.")
    calibrated_biases = reduced_images.files_filtered(imagetyp='Bias Frame', include_path=True)
    combined_bias = ccdp.combine(calibrated_biases,
                                 method='average',
                                 sigma_clip=True, sigma_clip_low_thresh=5, sigma_clip_high_thresh=5,
                                 sigma_clip_func=np.ma.median, sigma_clip_dev_func=mad_std,
                                 mem_limit=4e9, unit="adu", dtype='float32'
                                 )
    combined_bias.meta['combined'] = True
    combined_bias.write(calMastersPath / 'master_bias.fits')

# #
# # debias the dark frames, generate a master
# #
#
darkTempPath = Path('.', 'darkBiasSub-temp')
darkTempPath.mkdir(exist_ok=True)
darkFramesRaw = reduced_images.files_filtered(imagetyp='Dark Frame', include_path=False)

fileCheck = Path(calMastersPath / 'combined_dark_600.000.fits')
if fileCheck.exists():
    print('combined_dark_600.000.fits exists, reading.')
    #    combined_bias.read(calibrated_path / 'master_bias.fits')
    combined_dark = ccdp.CCDData.read(calMastersPath / 'combined_dark_600.000.fits', unit="adu")
else:
    print("combined_dark_600.000.fits does not exist, generating.")

    for file_name in darkFramesRaw:
        ccd = ccdp.CCDData.read(calibratorsPath / file_name, unit="adu")

        # Subtract bias
        ccd = ccdp.subtract_bias(ccd, combined_bias)
        # Save the result
        ccd.write(darkTempPath / file_name)

    darkImages = ccdp.ImageFileCollection(darkTempPath)
    darkFramesBiasSub = darkImages.files_filtered(imagetyp='Dark Frame', include_path=False)

    darks = darkImages.summary['imagetyp'] == 'Dark Frame'
    dark_times = set(darkImages.summary['exptime'][darks])
    print("Dark time: ", dark_times, " sec")

    for exp_time in sorted(dark_times):
        calibrated_darks = darkImages.files_filtered(imagetyp='Dark Frame', exptime=exp_time,
                                                         include_path=True)

        combined_dark = ccdp.combine(calibrated_darks,
                                     method='median',
                                     sigma_clip=True, sigma_clip_low_thresh=5, sigma_clip_high_thresh=5,
                                     sigma_clip_func=np.ma.median, sigma_clip_dev_func=mad_std,
                                     mem_limit=4e9, unit="adu", dtype='float32'
                                    )

        combined_dark.meta['combined'] = True

        dark_file_name = 'combined_dark_{:6.3f}.fits'.format(exp_time)
        combined_dark.write(calMastersPath / dark_file_name)


#
# Let's now build up the flat fields
#
print("Building flat fields.")
flatsPath = Path('AutoFlat')
flats_images = ccdp.ImageFileCollection(flatsPath)

flatTempPath = Path('.', 'flat-temp')
flatTempPath.mkdir(exist_ok=True)
flatFramesRaw = flats_images.files_filtered(imagetyp='Flat Field', include_path=False)

if 1:                                        # left this in to provide room for checking if flats were already generated
    print("Biasing/darking individual flats.")
    for file_name in flatFramesRaw:
        fileCheck = Path(flatTempPath / file_name)
        if fileCheck.exists():
            print('exists, skipping individual file ',file_name)
            #    combined_bias.read(calibrated_path / 'master_bias.fits')
        else:
            ccd = ccdp.CCDData.read(flatsPath / file_name, unit="adu")

            # Subtract the bias
            ccd = ccdp.subtract_bias(ccd, combined_bias)

            # Subtract dark current, scaled to exptime
            ccd = ccdp.subtract_dark(ccd, combined_dark,
                exposure_time='exptime', exposure_unit=u.second, scale=True)

            # Save the result
            ccd.write(flatTempPath / file_name)
    #
    # OK, now let's go filter by filter
    #
    flat_imagetyp = 'Flat Field'
    flatImages = ccdp.ImageFileCollection(flatTempPath)
    flat_filters = set(h['filter'] for h in flatImages.headers(imagetyp=flat_imagetyp))

    def inv_median(a):
        return 1 / np.median(a)

    for filt in flat_filters:
        print("Building flat for filter ",filt)
        flat_file_name = 'combined_flat_filter_{}.fits'.format(filt.replace("''", "p"))
        fileCheck = Path(calMastersPath / flat_file_name)
        if fileCheck.exists():
            print('exists, skipping')
        else:
            to_combine = flatImages.files_filtered(imagetyp=flat_imagetyp, filter=filt, include_path=True)
            combined_flat = ccdp.combine(to_combine,
                                         method='average', scale=inv_median,
                                         sigma_clip=True, sigma_clip_low_thresh=5, sigma_clip_high_thresh=5,
                                         sigma_clip_func=np.ma.median, sigma_clip_dev_func=mad_std,
                                         mem_limit=4e9, dtype='float32'
                                         )
            combined_flat.meta['combined'] = True
            combined_flat.write(calMastersPath / flat_file_name)

#
# OK now onto the science frames
#

science_imagetyp = 'Light Frame'
flat_imagetyp = 'Flat Field'
exposure = 'exposure'


for filt in flat_filters:
    fileCheck = Path(filt)
    if fileCheck.exists():
        print("Bias/dark/flat for science frames in ", filt)
        filterOutputPath = Path(filt, 'pipelineout-ccdproc')
        filterOutputPath.mkdir(exist_ok=True)

        ifc_reduced = ccdp.ImageFileCollection(filterOutputPath)
        ifc_raw = ccdp.ImageFileCollection(filt)
        lightFramesRaw = ifc_raw.files_filtered(imagetyp='Light Frame', include_path=False)

        ifc_calMasters = ccdp.ImageFileCollection(calMastersPath)
        lights = ifc_raw.summary[ifc_raw.summary['imagetyp'] == science_imagetyp.upper()]
        combo_calibs = ifc_calMasters.summary[ifc_calMasters.summary['combined'].filled(False).astype('bool')]

        print("loading dark")
        combined_darks = {ccd.header[exposure]: ccd for ccd in ifc_calMasters.ccds(imagetyp='Dark Frame', combined=True)}

        print("loading flat")
        combined_flats = {ccd.header['filter']: ccd for ccd in ifc_calMasters.ccds(imagetyp=flat_imagetyp, combined=True)}
        
        print("loading bias")
        # There is only one bias, so no need to set up a dictionary.
        combined_bias = [ccd for ccd in ifc_calMasters.ccds(imagetyp='Bias Frame', combined=True)][0]

        filterPath = Path(filt)

        for file_name in lightFramesRaw:

            ccd = ccdp.CCDData.read(filterPath / file_name, unit=u.adu)

            # Note that the first argument in the remainder of the ccdproc calls is
            # the *reduced* image, so that the calibration steps are cumulative.
            """
            reduced = ccdp.subtract_bias(ccd, combined_bias)

    #        closest_dark = find_nearest_dark_exposure(reduced, combined_darks.keys())

            reduced = ccdp.subtract_dark(reduced, combined_dark,
                                         exposure_time='exptime', exposure_unit=u.second)

            good_flat = combined_flats[reduced.header['filter']]
            reduced = ccdp.flat_correct(reduced, good_flat)
            reduced = ccdp.gain_correct(reduced, gain=2.19*u.electron/u.adu)
            """
            im_hdr = ccd[0].header
            im_exptime = im_hdr['exptime']
            
            dk_hdr = combined_dark[0].header
            dk_exptime = dk_hdr['exptime']

            good_flat = combined_flats[ccd.header['filter']]          
            reduced = ccdp.ccd_process(ccd, master_bias=combined_bias, dark_frame=combined_dark,
                                        master_flat=good_flat, gain=2.19*u.electron/u.adu,
                                        dark_exposure=dk_exptime*u.second, data_exposure=im_exptime*u.second,
                                        exposure_unit=u.second, readnoise=8.85, gain_corrected=False,
                                        dark_scale=True)
            
            #
            # should probably modify file_name to reflect changed nature with
            # '_proc' or something
            #

            # go from float64 to int16 to reduce the huuuuuuge filesize
            #
            #    type options: uint16, int16, int32, int64, float32, float64    
            #
            #reduced = CCDData_astype(reduced, dtype='int16')
            reduced = CCDData_astype(reduced, dtype='int32')

            reduced.write(filterOutputPath / file_name, overwrite=True)
    else:
        print("No bias/dark/flat for science frames in ", filt)
        
    # still need to clean up temp files
