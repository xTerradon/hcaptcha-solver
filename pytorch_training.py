import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as utils

from datetime import datetime as dt
import os
import pandas as pd
from copy import deepcopy as copy

import PIL

IMAGE_DIR = "./src/images/v1/"

class Training:
    def __init__(self):
        self.batch_size = 32
        self.test_batch_size = 1000
        self.lr = 0.001
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
            test_len = len(test_loader.dataset) - len(test_loader.dataset) % self.batch_size
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
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
    
    def predict(self, x):
        x = torch.from_numpy(x).float()
        with torch.no_grad():
            output = self.model(x)
            return output.round().detach().numpy()


def data_to_loader(x, y, test_split=0.25, batch_size=32):
    x_train = torch.from_numpy(x).float()
    y_train = torch.from_numpy(y).float()

    dataset = utils.TensorDataset(x_train, y_train)
    train_size = int((1 - test_split) * len(dataset))
    test_size = len(dataset) - train_size
    print(f"train size: {train_size}, test size: {test_size}")
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    train_loader = utils.DataLoader(train_dataset, batch_size=batch_size, drop_last=True, shuffle=True)
    test_loader = utils.DataLoader(test_dataset, batch_size=batch_size, drop_last=True, shuffle=True)

    print("single element shape:", train_loader.dataset[0][0].shape)

    return train_loader, test_loader


def train_model_on_captcha_string(db_handler, captcha_string=None, save=True):
    if captcha_string is None:
        captcha_string = db_handler.get_most_solved_captcha_string()
    print(f'Training model on {captcha_string}...')
    data = db_handler.get_solved_data(captcha_string, 1000)
    x = np.asarray([np.asarray(PIL.Image.open(open(IMAGE_DIR+path, 'rb'))) for path in data["path"]])
    x = x / 255 # norming
    x = np.moveaxis(x, [1,2,3], [2,3,1]) # color channel first
    # print(x[0])
    y = data["category"].values.reshape(-1,1)
    print(f"x shape: {x.shape}")
    print(f"y shape: {y.shape}")

    train_loader, test_loader = data_to_loader(x, y)

    training = Training()
    model = training.train(train_loader, test_loader)

    if save:
        now = dt.now().strftime("%y-%j")
        if not os.path.exists(f"./src/models/{captcha_string}"):
            os.makedirs(f"./src/models/{captcha_string}")
            i = 1
        else:
            i = len([a for a in os.listdir(f"./src/models/{captcha_string}") if now in a]) + 1
        path = f"./src/models/{captcha_string}/{now}_{i}"
        torch.save(model.state_dict(), path)
        print(f"Saved model to {path}")

def train_models_on_all_captcha_strings(db_handler, threshold=100, save=True):
    info = db_handler.get_info()
    info = info[info["solved"] >= threshold]
    captcha_strings = info.index.values
    for captcha_string in captcha_strings:
        train_model_on_captcha_string(db_handler, captcha_string, save=save)

    

def test_model_on_captcha_string(db_handler, captcha_string, model_name=None):
    if model_name is None:
        model_name = os.listdir(f"./src/models/{captcha_string}")[-1]
    model = Model(f"./src/models/{captcha_string}/{model_name}")

    print(f'Testing {model_name} on {captcha_string}...')
    data = db_handler.get_solved_data(captcha_string, 1000)
    x = np.asarray([np.asarray(PIL.Image.open(open(IMAGE_DIR+path, 'rb'))) for path in data["path"]])
    x = x / 255 # norming
    x = np.moveaxis(x, [1,2,3], [2,3,1]) # color channel first
    # print(x[0])
    y = data["category"].values.reshape(-1,1)

    pred = model.predict(x)
    df = pd.DataFrame({"pred": pred.reshape(-1).astype(int), "y": y.reshape(-1).astype(int)})
    df["correct"] = df["pred"] == df["y"]
    print(f"Correct: {df['correct'].sum()}/{len(df)}, Accuracy: {100.*df['correct'].sum()/len(df):.2f}%")
    return df

def test_models_on_all_captcha_strings(db_handler, threshold=100):
    captcha_strings = os.listdir("./src/models")
    ret = pd.Series([], name="cnn_accuracy", dtype=float)
    for captcha_string in captcha_strings:
        predictions = test_model_on_captcha_string(db_handler, captcha_string)
        s = pd.Series(predictions["correct"].sum()/len(predictions), index=[captcha_string], name="cnn_accuracy")
        ret = pd.concat((ret,s), axis=0)
    return ret