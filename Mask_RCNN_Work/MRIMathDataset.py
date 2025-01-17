'''
Created on Jun 18, 2018

@author: daniel
'''
import nibabel as nib
from mrcnn import utils
import skimage.color
import os
import numpy as np
from skimage import exposure
import SimpleITK as sitk

import matplotlib.pyplot as plt
import cv2

class MRIMathDataset(utils.Dataset):
    mode = None
    tumor_type = None

    def preprocess_image(self, image):
        
        sitk_image = sitk.GetImageFromArray(image)
        sitk_image = sitk.IntensityWindowing(sitk_image, np.percentile(image, 1), np.percentile(image, 99))
        sitk_image = sitk.Cast( sitk_image, sitk.sitkFloat64 )

        corrected_image = sitk.N4BiasFieldCorrection(sitk_image, sitk_image > 0);
        corrected_image = sitk.GetArrayFromImage(corrected_image)
        # corrected_image = exposure.equalize_hist(corrected_image)
        return corrected_image
        

    def load_image(self, image_id):
        ## Note:
        # FLAIR -> Whole
        # T2 -> Core
        # T1C -> Active (if present)
        """Load the specified image and return a [H,W,3] Numpy array.
        """
        info = self.image_info[image_id]
        for path in os.listdir(info['path']):
            if self.mode in path:
                image = nib.load(info['path'] + "/" + path).get_data()[:,:,info['ind']]
                break
        image = self.preprocess_image(image)
        if image.ndim != 3:
            image = image.astype(np.uint8)
            image = cv2.cvtColor(image,cv2.COLOR_GRAY2RGB)
            #image = skimage.color.gray2rgb(image)
        # If has an alpha channel, remove it for consistency
        if image.shape[-1] == 4:
            image = image[..., :3]
        return image
    
    def load_images(self, data_dir):
        print('Reading images')
        # Add classes
        self.add_class("mrimath", 1, self.tumor_type)
        i = 0
        for subdir in os.listdir(data_dir):
            indices = self.getIndicesWithTumorPresent(data_dir + "/" + subdir)
            for j in indices:
                self.add_image("mrimath", image_id=i, path=data_dir + "/" + subdir, ind = j)
                i = i + 1
        
    def image_reference(self, image_id):
        """Return the shapes data of the image."""
        info = self.image_info[image_id]
        if info["source"] == "mrimath":
            return info["source"]
        else:
            super(self.__class__).image_reference(self, image_id)
    
    def getIndicesWithTumorPresent(self, directory):
        indicesWithMasks = []
        path = next((s for s in os.listdir(directory) if "seg" in s), None)
        mask = nib.load(directory+"/"+path).get_data()
        for i in range(0,155):
            if np.count_nonzero(mask[:,:,i]) > 0:
                indicesWithMasks.append(i)
        return indicesWithMasks
        

    def load_mask(self, image_id):
        """Generate instance masks for shapes of the given image ID.
        """        
        for path in os.listdir(self.image_info[image_id]['path']):
            if "seg" in path:
                mask = nib.load(self.image_info[image_id]['path']+"/"+path).get_data()[:,:,self.image_info[image_id]['ind']]
                break
        """
        plt.figure(1)
        plt.imshow(mask)
        plt.show()
        """
        mask = self.getMask(mask)
        mask = mask.reshape(mask.shape[0], mask.shape[1],1)
        return mask.astype(bool), np.ones([mask.shape[-1]], dtype=np.int32)

    def getMask(self, mask):
        pass
        