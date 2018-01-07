'''
Created on Jan 1, 2018

@author: daniel
'''

import os
import cv2
import numpy as np
import multiprocessing
from joblib import Parallel, delayed





def getImage(self, path):
    path=path.decode()
    img = cv2.imread(path,0)
    return img

    
def loadIndividualImage(training_directory, j, X_train, segment_data):
        if((j>0 and j < 107) or j > 135):
            print('Reading Patient ' + str(j))
            if j < 10:
                directory = os.fsencode(training_directory + '/Patient_(00' + str(j)  + ')_data/')
            elif j < 100:
                directory = os.fsencode(training_directory + '/Patient_(0' + str(j)  + ')_data/')
            else:
                directory = os.fsencode(training_directory + '/Patient_(' + str(j)  + ')_data/')
            for file in os.listdir(directory + b'/Original_Img_Data'):
                img = getImage(directory+b'/Original_Img_Data/'+file)
                X_train.append(img)
                segment_directory = os.fsencode(directory + b'Segmented_Img_Data')
                for dir in os.listdir(segment_directory):
                    for file in os.listdir(segment_directory+b'/'+dir):
                        ind = file[4:5]
                        segment_data[int(ind.decode())-1].append(getImage(segment_directory+b'/'+dir+b'/'+file))



class DataHandler:
    
    W = 240
    H = 240


    def loadDataSequential(self, training_directory, start, finish):
        X_train = []
        segment_data = [[] for _ in range(8)]
        print('Reading images')
        for j in range(start,finish):
            loadIndividualImage(training_directory, j, X_train, segment_data)
        training, segments = self.preprocessForNetwork(X_train, segment_data)
        return training, segments
    
    def loadDataParallel(self, training_directory, start, finish):
        X_train = []
        segment_data = [[] for _ in range(8)]
        print('Reading images')
        num_cores = multiprocessing.cpu_count()
        Parallel(n_jobs=num_cores)(delayed(loadIndividualImage(training_directory, i, X_train, segment_data) for i in range(start, finish)))
    
        
    def preprocessForNetwork(self, training_data, segment_data):
        n_imgs = len(training_data)
        training = np.array(training_data)
        training = training.reshape(n_imgs,self.W,self.H,1)
        training = training.astype('float32') / 255;
        segments = np.array(segment_data);
        segments = segments.reshape(n_imgs,self.W,self.H,8)
        return training, segments
    

        
        