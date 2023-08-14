import nn_handler
import numpy as np

from PIL import Image
from io import BytesIO
from skimage.transform import resize

from difflib import SequenceMatcher

class Captcha_Solver:
    def __init__(self):
        self.nh = nn_handler.NN_Handler()
        available_models = self.nh.get_all_models()

    def get_images(self, raw_images):
        images = []
        for raw_image in raw_images:
            img = np.array(Image.open(BytesIO(raw_image)))
            if img.shape != (160,160,3):
                res = img.shape[0]
                img = resize(img, (160,160))
            else:
                img = img / 255

            images.append(img)
        
        images = np.array(images)
        return images
    
    def solve_captcha(self, captcha_string, raw_image_data):
        images = self.get_images(raw_image_data)
        predictions = self.nh.predict_images(captcha_string, images)
        print(np.round(predictions.reshape((3,3)),2))
        return (predictions > 0.5)

    def normalize_string(self, string):
        string = string.replace(" ","_")
        ratios = []
        for model_name in self.available_models:
            ratios.append(SequenceMatcher(a=string,b=model_name).ratio())
        print(ratios)
        if max(ratios) > 0.5:
            return self.available_models[np.argmax(np.array(ratios))]
        return ""
