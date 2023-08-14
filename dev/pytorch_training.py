import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as utils
import torch.nn.init as init

from datetime import datetime as dt
import os
import pandas as pd
from copy import deepcopy as copy

import PIL

IMAGES_DIR = "../data/images/v1/"
MODELS_DIR = "../data/models/"

class Training:
    def __init__(self):
        self.batch_size = 16
        self.test_batch_size = 1000
        self.lr = 0.0001
        self.log_interval = 1

        self.model = nn.Sequential(  
            nn.Conv2d(3, 16, kernel_size=7, padding=3),  
            nn.ReLU(),  
            nn.MaxPool2d(2, stride=2),  
            nn.Conv2d(16, 32, kernel_size=5, padding=2),  
            nn.ReLU(),  
            nn.MaxPool2d(2, stride=2),  
            nn.Conv2d(32, 64, kernel_size=3, padding=1),  
            nn.ReLU(),  
            nn.MaxPool2d(2, stride=2),  
            nn.Flatten(),  
            nn.Linear(16384, 128),  
            nn.ReLU(),  
            nn.Linear(128, 1),  
            nn.Sigmoid()  
        )  

        # Initialize weights using Xavier/Glorot initialization
        for layer in self.model:
            if isinstance(layer, nn.Linear):
                init.xavier_uniform_(layer.weight)

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.criterion = nn.BCELoss()

    def train(self, train_loader, test_loader, verbose=True, epochs=50, early_stopping=10):
        losses = []
        early_stopping_counter = 0
        best_model = None
        for epoch in range(1, epochs + 1):
            # training
            self.model.train()
            for batch_idx, (data, target) in enumerate(train_loader):
                self.optimizer.zero_grad()
                output = self.model(data)
                loss = self.criterion(output, target)
                loss.backward()
                self.optimizer.step()

            # testing
            self.model.eval()
            test_loss = 0
            correct = 0
            with torch.no_grad():
                for i, (data, target) in enumerate(test_loader):
                    output = self.model(data)
                    test_loss += self.criterion(output, target).item()
                    pred = output.round()
                    correct += pred.eq(target.view_as(pred)).sum().item()
            test_len = len(test_loader.dataset)
            test_loss /= test_len
            losses.append(test_loss)
            if verbose : print(f'Epoch: {epoch}, Test Loss: {test_loss:.4f}, Accuracy: {correct}/{test_len}, {100. * correct / test_len:.2f}%')

            if len(losses) > 0 and test_loss > min(losses):
                early_stopping_counter += 1
                if early_stopping_counter >= early_stopping:
                    print(f"Early stopping at epoch {epoch}")
                    break
            else:
                early_stopping_counter = 0
                best_model = copy(self.model)

        self.model = best_model
        return self.model

class Model:
    def __init__(self, model_path):
        self.model = torch.load(model_path)
        self.model.eval()
    
    def predict(self, x):
        x = torch.from_numpy(x).float()
        with torch.no_grad():
            output = self.model(x)
            return output.round().detach().numpy()


def data_to_loader(x, y, test_split=0.25, batch_size=16):
    assert len(x) == len(y), "x and y must have the same length"
    assert len(x) >= 64, "at least 64 samples required for training"

    x_train = torch.from_numpy(x).float()
    y_train = torch.from_numpy(y).float()

    dataset = utils.TensorDataset(x_train, y_train)
    test_size = int(len(dataset) * test_split)
    train_size = len(dataset) - test_size

    overhang = train_size % batch_size
    train_size -= overhang
    test_size += overhang

    print(f"train size: {train_size}, test size: {test_size}")
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    train_loader = utils.DataLoader(train_dataset, batch_size=batch_size, drop_last=True, shuffle=True)
    test_loader = utils.DataLoader(test_dataset, batch_size=test_size, drop_last=True, shuffle=True)

    print("single element shape:", train_loader.dataset[0][0].shape)

    return train_loader, test_loader


def train_model_on_captcha_string(db_handler, captcha_string=None, save=True):
    if captcha_string is None:
        captcha_string = db_handler.get_most_solved_captcha_string()
    print(f'Training model on {captcha_string}...')
    
    x,y = get_image_data(db_handler, captcha_string)

    train_loader, test_loader = data_to_loader(x, y)

    training = Training()
    model = training.train(train_loader, test_loader)

    if save:
        now = dt.now().strftime("%y-%j")
        if not os.path.exists(f"{MODELS_DIR}{captcha_string}"):
            os.makedirs(f"{MODELS_DIR}{captcha_string}")
            i = 1
        else:
            i = len([a for a in os.listdir(f"{MODELS_DIR}{captcha_string}") if now in a]) + 1
        path = f"{MODELS_DIR}{captcha_string}/{now}_{str(i).zfill(2)}"
        torch.save(model, path)
        print(f"Saved model to {path}")

def train_models_on_all_captcha_strings(db_handler, threshold=100, save=True):
    info = db_handler.get_info()
    info = info[info["solved"] >= threshold]
    captcha_strings = info.index.values
    for captcha_string in captcha_strings:
        train_model_on_captcha_string(db_handler, captcha_string, save=save)

    
def get_image_data(db_handler, captcha_string):
    data = db_handler.get_solved_data(captcha_string, 1000)

    images_raw = [np.asarray(PIL.Image.open(open(IMAGES_DIR+path, 'rb'))) for path in data["path"]]
    useable_indexes = [i for i in range(len(images_raw)) if images_raw[i].shape == (128,128,3)]

    useable_images = [images_raw[i] for i in useable_indexes]

    print(f"Fount {len(useable_images)} useable images")

    x = np.asarray(useable_images)
    x = x / 255 # norming
    x = np.moveaxis(x, [1,2,3], [2,3,1]) # color channel first
    # print(x[0])
    y = data["category"][useable_indexes].values.reshape(-1,1)
    print(f"x shape: {x.shape}")
    print(f"y shape: {y.shape}")

    return x, y

def test_model_on_captcha_string(db_handler, captcha_string, model_name=None):
    if model_name is None:
        model_name = os.listdir(f"{MODELS_DIR}{captcha_string}")[-1]
    model = Model(f"{MODELS_DIR}{captcha_string}/{model_name}")

    print(f'Testing {model_name} on {captcha_string}...')
    x, y = get_image_data(db_handler, captcha_string)

    pred = model.predict(x)
    df = pd.DataFrame({"pred": pred.reshape(-1).astype(int), "y": y.reshape(-1).astype(int)})
    df["correct"] = df["pred"] == df["y"]
    print(f"Correct: {df['correct'].sum()}/{len(df)}, Accuracy: {100.*df['correct'].sum()/len(df):.2f}%")
    return df

def test_models_on_all_captcha_strings(db_handler, threshold=100):
    captcha_strings = os.listdir(MODELS_DIR)
    ret = pd.Series([], name="cnn_accuracy", dtype=float)
    for captcha_string in captcha_strings:
        predictions = test_model_on_captcha_string(db_handler, captcha_string)
        s = pd.Series(predictions["correct"].sum()/len(predictions), index=[captcha_string], name="cnn_accuracy")
        ret = pd.concat((ret,s), axis=0)
    return ret