import numpy as np
import requests
from PIL import Image
from transformers import ViTFeatureExtractor, ViTForImageClassification


class Image_Classifier:
    def __init__(self):
        self.feature_extractor = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-224')
        self.model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

    def get_predictions_from_url(self, url):
        print("IMAGE at", url)
        raw_data = requests.get(url, stream=True).raw

        image = Image.open(raw_data)

        inputs = self.feature_extractor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)
        logits = outputs.logits
        predictions = logits.sort(-1)[1].numpy()[0]

        print([self.model.config.id2label[b] for b in predictions[-5:]])

        return predictions
    
    def get_predictions_from_urls(self, urls):
        predictions = []
        for url in urls:
            predictions.append(self.get_predictions_from_url(url))
        return np.array(predictions)
