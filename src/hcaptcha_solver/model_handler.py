import numpy as np
import torch

from PIL import Image
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(CURRENT_DIR, 'models/')

class Model:
    def __init__(self, name):
        self.model = torch.load(MODELS_DIR + name)
        self.model.eval()

    def predict(self, x):
        x = torch.from_numpy(x).float()
        with torch.no_grad():
            return self.model(x).detach().numpy().flatten()
            
    
class Model_Handler:
    def __init__(self):
        print("Initializing model handler...")
        self.models = {}
        for model_name in os.listdir(MODELS_DIR):
            try:
                self.models[model_name] = Model(model_name)
            except Exception as e:
                print(f"Failed to load model {model_name}")
                print(e)
        print(f"Loaded {len(self.models)} models")
    
    def get_labels(self, captcha_string : str, pil_images : list):
        print(f"Predicting {len(pil_images)} images...")

        x = self.preprocess_pil_images(pil_images)
        y = list(self.models[captcha_string].predict(x))

        print(f"Predictions: {y}")

        is_correct = [prediction > 0.5 for prediction in y]

        print(f"Correct Images: {is_correct}")

        return is_correct

    def preprocess_pil_images(self, pil_images : list):
        x = np.asarray([np.asarray(img) for img in pil_images]) / 255 # norming [0,1]
        x = np.moveaxis(x, [1,2,3], [2,3,1]) # color channel first
        return x