'''
Created on Jan 9, 2018

@author: daniel
'''


from TimerModule import TimerModule
from keras.callbacks import CSVLogger
from tensorflow.python.client import device_lib
from keras.models import Model
import os
from EmailHandler import EmailHandler
from datetime import datetime
from keras.utils.training_utils import multi_gpu_model
import tensorflow as tf
from DataHandler import DataHandler
from ConvolutionalEncoder import ConvolutionalEncoder


def getAvailableGPUs():
    local_device_protos = device_lib.list_local_devices()
    return len([x.name for x in local_device_protos if x.device_type == 'GPU'])

now = datetime.now()
date_string = now.strftime('%Y_%m_%d')
dataHandler = DataHandler()
emailHandler = EmailHandler()
timer = TimerModule()
model = ConvolutionalEncoder([120,60,30,15,15,30,60,120])
input_img, output = model.getModel()

data_dir = '/coe_data/MRIMath/MS_Research/Patient_Data_Images'
#data_dir = '/media/daniel/ExtraDrive1/Patient_Data_Images'
training, segments = dataHandler.loadDataParallel(data_dir, 1, 107)
testing, segments2 = dataHandler.loadDataParallel(data_dir,136,167)

model_directory = "/coe_data/MRIMath/MS_Research/MRIMath/Models/" + date_string
if not os.path.exists(model_directory):
    os.makedirs(model_directory)
    
G = getAvailableGPUs()
num_epochs = 1
batchSize = 32
segmentation_bank = [[] for _ in range(8)]
for i in range(0,8):
    specific_model_directory = model_directory + '/' + 'Model ' + str(i)
    if not os.path.exists(specific_model_directory):
        os.makedirs(specific_model_directory)
    
    model_info_filename = 'model_'+str(i) +"_"+ "info.txt"
    model_info_file = open(specific_model_directory + '/' + model_info_filename,"w") 
    log_info_filename = 'model_' + str(i) + '_loss_log.csv'
    log_info = open(specific_model_directory + '/' + log_info_filename, "w")
    
    train_segment = segments[:,:,:,i:i+1]
    test_segment = segments2[:,:,:,i:i+1]
    
    print('Training network: ' + str(i))
    csv_logger = CSVLogger(specific_model_directory + '/' + log_info_filename, append=True, separator=';')
    print('Using ' + str(G) + ' GPUs to train the network!')
    if G > 1:
        with tf.device('/cpu:0'):
            segmentation_bank[i] = Model(input_img, output)
        parallel_segmentation_bank = multi_gpu_model(segmentation_bank[i], G)
        parallel_segmentation_bank.compile(optimizer='nadam', loss='mean_squared_error')
        timer.startTimer()
        parallel_segmentation_bank.fit(training, train_segment,
                epochs=num_epochs,
                batch_size=batchSize*G,
                shuffle=True,
                validation_data=(testing, test_segment),
                callbacks=[csv_logger])
        timer.stopTimer()
        
    else:
        segmentation_bank[i] = Model(input_img, output)
        segmentation_bank[i].compile(optimizer='adam', loss='mean_squared_error')
        timer.startTimer()
        segmentation_bank[i].fit(training, train_segment,
                epochs=num_epochs,
                batch_size=batchSize*G,
                shuffle=True,
                validation_data=(testing, test_segment),
                callbacks=[csv_logger])
        timer.stopTimer()
            
    segmentation_bank[i].set_weights(parallel_segmentation_bank.get_weights())
    print('Saving model ' + str(i) + ' to disk!')
    segmentation_bank[i].save(specific_model_directory + '/model_' + str(i) +'.h5')
    
    emailHandler.connectToServer()
    message = "Finished training network " + str(i) + " at " + str(datetime.now()) + '\n\n'
    message += 'The network was trained on ' + str(training.shape[0]) + ' images \n\n'
    message += 'The network was validated on ' + str(testing.shape[0]) + ' images \n\n'
    message += "The network was trained for " + str(num_epochs) + " epochs with a batch size of " + str(batchSize) + '\n\n'
    message += "The model was saved to " + specific_model_directory + '\n'
    
    segmentation_bank[i].summary(print_fn=lambda x: model_info_file.write(x + '\n'))
    message += "\n Total training time: " + str(timer.getElapsedTime())
    emailHandler.prepareMessage(date_string + " MRIMath Update: Network Training Finished!", message);
    model_info_file.close()
    emailHandler.attachFile(model_info_file, model_info_filename)
    emailHandler.attachFile(log_info, log_info_filename)
    emailHandler.sendMessage("Danny")
    emailHandler.finish()






