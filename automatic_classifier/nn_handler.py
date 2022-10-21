import os

import tensorflow as tf


class NN_Handler:
    def __init__(self):
        self.models = {}
        try:
            model_strings = os.listdir("/models/")
            print("Loaded Models:", model_strings)
        except:
            print("Models coult not be read")
        
        for model_string in model_strings:
            self.models[model_string] = tf.keras.models.model_load("/models/"+model_string)

    def predict_images(self, captcha_string, images):
        if captcha_string in self.models.keys():
            print("Using model",captcha_string,"to predict",len(images),"Images")
            model = self.models[captcha_string]
            predictions = np.array(model.predict(images))[:,0]
            print(predictions.reshape((3,3)))
            print(np.array(predictions > 0.5).reshape((3,3)))
            return predictions

        
