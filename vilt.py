from transformers import ViltProcessor, ViltForQuestionAnswering, TrainingArguments, Trainer
import requests
import os
import pandas as pd
from PIL import Image
import torch

IMAGE_DIR = "src/images/v1/"

class Vilt_Classifier:
    def __init__(self):
        self.model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
        self.processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
        self.labels = self.model.config.id2label

    def predict_by_paths(self, captcha_string, paths):
        question = f"Does this image contain a {captcha_string}? yes or no:"
        images = [Image.open(IMAGE_DIR+path) for path in paths]

        encoding = self.processor(text=[question]*len(images), images=images, return_tensors="pt")
        outputs = self.model(**encoding)

        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)

        return [True if v=="yes" else False for v in [self.labels[prediction.item()] for prediction in predictions]]

    def get_accuracy_by_captcha(self, db_handler, captcha_string):
        data = db_handler.get_solved_data(captcha_string, 1000)
        print(f"Calculating accuracy for {captcha_string} using {len(data)} images")

        predictions = self.predict_by_paths(captcha_string, data["path"])
        data["predicted"] = pd.Series(predictions, dtype=int)
        data["correct"] = data["predicted"] == data["category"]
        data

        return data["correct"].mean()

    def get_accuracy_for_all_captchas(self, db_handler, threshold=50):
        info = db_handler.get_info()
        info = info[info["solved"] >= threshold]
        captcha_strings = info.index.values
        print(f"Calculating accuracy for {len(captcha_strings)} captchas which satisfied the threshold of {threshold} solved images")

        info["accuracy"] = [self.get_accuracy_by_captcha(db_handler, cs) for cs in captcha_strings]
        return info

    def finetune_vilt(self, db_handler):
        # TODO: finetuning here
        train_data = db_handler.get_solved_data("helicopter",100)

        print("train data", train_data)
        train_args = TrainingArguments("test_trainer")
        trainer = Trainer(
            model=self.model,
            args=train_args,
            train_dataset=train_data
        )