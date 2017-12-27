'''
Created on Nov 28, 2017

@author: daniel
'''


from keras.models import load_model
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt



def get_im(path):
    path=path.decode()
    img = cv2.imread(path,0)
    return img

training_directory = '/media/daniel/ExtraDrive1/Patient_Data_Images';
segment_number = 1;
k = 1;
model = load_model('/media/daniel/ExtraDrive1/model_' + str(segment_number) + '_seg2.h5')
#X_test = []

for j in range(11,20):
        print('Reading Patient ' + str(j))
        if j < 10:
            directory = os.fsencode(training_directory + '/Patient_(00' + str(j)  + ')_data/')
        elif j < 100 and j>10:
            directory = os.fsencode(training_directory + '/Patient_(0' + str(j)  + ')_data/')

        else:
            directory = os.fsencode(training_directory + '/Patient_(' + str(j)  + ')_data/')
        for file in os.listdir(directory + b'/Original_Img_Data'):
            seg_directory = os.fsencode(training_directory + '/Patient_(0' + str(j)  + ')_data/Segmented_Img_Data/img_'+str(k))
            img = get_im(directory+b'/Original_Img_Data/'+file)
            seg_img = get_im(seg_directory+b'/seg_1.png')
            X_seg = np.array(seg_img)
            print(seg_directory)
            X_seg = X_seg.reshape(1,240,240,1)
            X_test = np.array(img)
            X_test = X_test.reshape(1,240,240,1)
            X_test = X_test.astype('float32') / 255
            y = model.predict(X_test)
            fig = plt.figure()
            plt.gray();
            a=fig.add_subplot(1,3,1)
            plt.imshow(img)
            a=fig.add_subplot(1,3,2)
            plt.imshow(seg_img)
            a=fig.add_subplot(1,3,3)
            plt.imshow(y.reshape(240,240))
            plt.show();
            k = k+1;

