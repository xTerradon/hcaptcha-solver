import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as utils
from torch.nn import init

from datetime import datetime as dt
import os
import pandas as pd
from copy import deepcopy as copy

import PIL

  
class EuclideanDistanceLoss(nn.Module):  
    def __init__(self):  
        super(EuclideanDistanceLoss, self).__init__()  
  
    def forward(self, output, target):  
        assert output.size() == target.size()  
  
        squared_diff = (output - target) ** 2  
  
        sum_squared_diff = torch.sum(squared_diff, dim=1)  
        euclidean_distance = torch.sqrt(sum_squared_diff)  
  
        loss = torch.mean(euclidean_distance)  
  
        return loss  


class Model_Training:
    def __init__(self):
        self.batch_size = 64
        self.lr = 0.0001
        self.log_interval = 1

        self.model = nn.Sequential(  
            nn.Conv2d(4, 16, kernel_size=7, padding=3),  
            nn.ReLU(),  
            nn.MaxPool2d(2, stride=2),  
            nn.Conv2d(16, 32, kernel_size=5, padding=2),  
            nn.ReLU(),  
            nn.MaxPool2d(2, stride=2),  
            nn.Conv2d(32, 64, kernel_size=3, padding=1),  
            nn.ReLU(),  
            nn.MaxPool2d(2, stride=2),  
            nn.Flatten(),  
            nn.Linear(265856 , 128),  
            nn.ReLU(),  
            nn.Linear(128, 2),  
            nn.Tanh()
        )  

        # Initialize weights using Xavier/Glorot initialization
        for layer in self.model:
            if isinstance(layer, nn.Linear):
                init.xavier_uniform_(layer.weight)

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.criterion = EuclideanDistanceLoss()

    def train(self, db2, epochs=10, verbose=True):
        x, y = get_image_data(db2)
        train_loader, test_loader = self.data_to_loader(x, y, batch_size=self.batch_size)
        self.model = self.training_loop(train_loader, test_loader, verbose=verbose, epochs=epochs)
        return self.model

    def data_to_loader(self, x, y, test_split=0.25, batch_size=16):
        assert len(x) == len(y), "x and y must have the same length"
        
        test_length = len(x_test)

        x = torch.from_numpy(x).float()
        y = torch.from_numpy(y).float()

        dataset = utils.TensorDataset(x, y)
        test_size = int(len(dataset) * test_split)
        train_size = len(dataset) - test_size

        overhang = train_size % batch_size
        train_size -= overhang
        test_size += overhang

        train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])


        train_loader = utils.DataLoader(dataset_train, batch_size=batch_size, drop_last=True, shuffle=True)
        test_loader = utils.DataLoader(dataset_train, batch_size=test_length, drop_last=True, shuffle=False)

        print("single element shape:", train_loader.dataset[0][0].shape)

        return train_loader, test_loader

    def training_loop(self, train_loader, test_loader, verbose=True, epochs=50):
        losses = []
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
            with torch.no_grad():
                for i, (data, target) in enumerate(test_loader):
                    output = self.model(data)
                    test_loss += self.criterion(output, target).item()

            if verbose and epoch % (epochs // 10) == 0: print(f'Epoch: {epoch}, Test Loss: {test_loss:.4f}')

        return self.model

    def predict_pil(self, pil_images):
        if not isinstance(pil_images, list):
            pil_images = [pil_images]
        preprocessed_images = preprocess_pil(pil_images)
        return self.predict(preprocessed_images)

    def predict(self, x):
        x = torch.from_numpy(x).float()
        with torch.no_grad():
            output = self.model(x)
            return output.detach().numpy()

class Loaded_Model:
    def __init__(self, model_path):
        self.model = torch.load(model_path)
        self.model.eval()
    
    def predict(self, x):
        x = torch.from_numpy(x).float()
        with torch.no_grad():
            output = self.model(x)
            return output.round().detach().numpy()

def get_image_data(db2):
    image_paths, positions = db2.get_captchas()

    images_raw = [np.asarray(PIL.Image.open(open(path, 'rb'))) for path in image_paths]
    print("shapes:", [a.shape for a in images_raw])

    useable_indexes = [i for i in range(len(images_raw)) if images_raw[i].shape == (536, 500, 4)]
    useable_images = [images_raw[i] for i in useable_indexes]
    print(f"Fount {len(useable_images)} useable images")

    return preprocess_pil(useable_images)

def preprocess_pil(images):
    x = np.asarray(images)
    x = x / 255 # norming
    x = np.moveaxis(x, [1,2,3], [2,3,1]) # color channel first
    # print(x[0])
    print(f"x shape: {x.shape}")

    return x