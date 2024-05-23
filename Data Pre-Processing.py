### Saved as ~/UKIDSSxIRAC/prep_fits_to_npy.py
import numpy as np
import matplotlib.pyplot as plt
import os, time, glob, copy

from astropy.io import fits

import cv2
import argparse

# ------- Edit it to recieve variables from the config.py ------- #
root_dir = os.getcwd() # /home/jiwon/UKIDSSxIRAC

survey1 = 'ukidss'
filters1 = ['J', 'H', 'K']

survey2 = 'spitzer'
filters2 = ['ch1', 'ch2', 'ch3', 'ch4']

train_ratio = 0.6
val_ratio = 0.2
test_ratio = 0.2

# --------------------------------------------------------------- #

data_dir1 = os.path.join(root_dir,'images',survey1)
# datalist1 = [os.path.splitext(os.path.abspath(x))[0] for x in glob.glob(os.path.join(data_dir1,'*_J.fits'))]
datalist1 = [os.path.abspath(x) for x in glob.glob(os.path.join(data_dir1,'*.fits'))]
datalist1.sort()
# imglist1 = [os.path.basename(x) for x in datalist1]

data_dir2 = os.path.join(root_dir,'images',survey2)
# datalist2 = [os.path.splitext(os.path.abspath(x))[0] for x in glob.glob(os.path.join(data_dir2,'*_ch1.fits'))]
datalist2 = [os.path.abspath(x) for x in glob.glob(os.path.join(data_dir2,'*.fits'))]
datalist2.sort()
# imglist2 = [os.path.basename(x) for x in datalist2]

class FitsArrayConverter:
    def __init__(self, filename):
        self.filename = filename    

    def get_image(self):
        file = fits.open(self.filename)
        # file.info() ###
        image = copy.deepcopy(file[0].data)     # type(image): numpy.ndarray
        return image

    def resize(self, org_array, edit_pix):
        return cv2.resize(org_array, (edit_pix, edit_pix))
    
    def upsample(self, org_array, num):
        return org_array.repeat(num, axis=0).repeat(num, axis=1)

    def save_as_npy(self, image, pre_processed=''):
        savename = root_dir+'/data/'+self.filename.split('images/')[1]
        np.save(os.path.splitext(savename)[0]+pre_processed+'.npy', image)
    
    def save_image(self, size_fit=True, size_pix=60, upsample=False, up_num=1, marking=False, verbose=False):
        image = self.get_image()
        org_size = np.shape(image)

        pre_processed = ''
        if size_fit:
            image = self.resize(image, size_pix)
            pre_processed = pre_processed+'_resized'
        if upsample:
            image = self.upsample(image, up_num)
            pre_processed = pre_processed+'_upsampled'
        if not marking:
            pre_processed = ''
        if verbose:
            filter = os.path.splitext(self.filename)[0].split('_')[-1]
            print(f'{filter}:   {org_size}  ==>  {np.shape(image)}')

        self.save_as_npy(image, pre_processed)

if not os.path.exists(root_dir+'/data'):
    print(f'\n=== Making "data" Directory ===\n')
    os.makedirs(root_dir+'/data')
    os.makedirs(root_dir+'/data/'+survey1)
    os.makedirs(root_dir+'/data/'+survey2)
    for i in range(len(filters1)):
        print(os.path.join(root_dir,'data',survey1,filters1[i]))
        # os.makedirs(os.path.join(root_dir,'data',survey1,filters1[i]))    

print('\n###--- Image Pre-processing: UKIDSS ---###')
for i in range(len(datalist1)): 
    verbose = False     ### Check!
    if verbose:     
        if i%len(filters1) == 0:
            print('\n'+'[[ # '+os.path.basename(datalist1[i]).split('_')[-2]+' ]]')
    imgarray1 = FitsArrayConverter(datalist1[i])
    imgarray1.save_image(size_fit=True, size_pix=300, upsample=False, up_num=1, verbose=verbose)

print('Completed to save as .npy file')
print()
print('\n###---  Image Pre-processing: IRAC  ---###')

for i in range(len(datalist2)): 
    verbose = False     ### Check!
    if verbose: 
        if i%len(filters2) == 0:
            print('\n'+'[[ # '+os.path.basename(datalist2[i]).split('_')[-2][1:]+' ]]')

    imgarray2 = FitsArrayConverter(datalist2[i])
    imgarray2.save_image(size_fit=True, size_pix=60, upsample=True, up_num=5, verbose=verbose)
    
print('Completed to save as .npy file')
