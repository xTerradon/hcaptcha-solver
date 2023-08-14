import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2" 

import tensorflow as tf
import numpy as np

import pathlib


class NN_Handler:
    def __init__(self):
        self.models = {}
        model_dir = str(pathlib.Path(__file__).parent.resolve()).split("\\captcha_handler")[0]+"\\models\\"
        try:
            model_strings = os.listdir(model_dir)
            print("Loaded Models:", model_strings)
        except:
            print("Models could not be read")
            return
        
        for model_string in model_strings:
            self.models[model_string] = tf.keras.models.load_model(model_dir+model_string)

    def predict_images(self, captcha_string, images):
        if captcha_string in self.models.keys():
            print("Using model",captcha_string,"to predict",len(images),"Images")
            model = self.models[captcha_string]
            predictions = np.array(model.predict(images))[:,0]
            return predictions
        else:
            print("No model found for",captcha_string)
            return None
        
    def has_model(self, captcha_string):
        return captcha_string in self.models.keys()
    
    def get_all_models(self):
        return list(self.models.keys())

        
