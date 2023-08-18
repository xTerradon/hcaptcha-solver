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

from PIL import Image
from matplotlib import pyplot as plt

IMAGES_DIR_V2 = "../../data/images/v2/"
CLICKABLE_AREA_BOUNDARIES = (83,194,417,527)
CLICKABLE_AREA_SIZE = (CLICKABLE_AREA_BOUNDARIES[2] - CLICKABLE_AREA_BOUNDARIES[0], CLICKABLE_AREA_BOUNDARIES[3] - CLICKABLE_AREA_BOUNDARIES[1])

class CustomMSE(nn.Module):  
    def __init__(self):  
        super(CustomMSE, self).__init__()  
  
    def forward(self, output, target, verbose=False):  
        assert output.size() == target.size()  
  
        squared_diff = (output - target) ** 2
        
        # clickable = target > 0.2
        # squared_diff[clickable] *= 10 # 5, 10, 20

        squared_diff *= (target + 0.05) # 0.1, 0.2

        return torch.mean(squared_diff)

class Model_Training:
    def __init__(self, grid_size=16):
        self.grid_size = grid_size
        self.batch_size = 16
        self.lr = 0.001
        self.log_interval = 1
        
        # Define your convolutional layers  
        self.model = nn.Sequential(  
            nn.Conv2d(3, 16, kernel_size=7, padding=3),  
            # nn.BatchNorm2d(16),  
            nn.ReLU(),  
            nn.MaxPool2d(2, stride=2),  
            nn.Conv2d(16, 32, kernel_size=5, padding=2),  
            # nn.BatchNorm2d(32), 
            nn.ReLU(),  
            nn.MaxPool2d(2, stride=2),  
            nn.Conv2d(32, 64, kernel_size=3, padding=1),  
            # nn.BatchNorm2d(64),   
            nn.ReLU(),   
            nn.Conv2d(64, 32, kernel_size=3, padding=1),  
            # nn.BatchNorm2d(32), 
            nn.ReLU(),   
            nn.Conv2d(32, 16, kernel_size=3, padding=1),  
            # nn.BatchNorm2d(16), 
            nn.ReLU(), 
            nn.Conv2d(16, 1, kernel_size=1, padding=0),  
            nn.AdaptiveMaxPool2d((grid_size, grid_size)), 
            nn.Sigmoid()
        )  

        # Initialize weights using Xavier/Glorot initialization  
        for layer in self.model:  
            if isinstance(layer, nn.Linear) or isinstance(layer, nn.Conv2d):  
                init.xavier_uniform_(layer.weight)  
            elif isinstance(layer, nn.BatchNorm2d):  
                init.constant_(layer.weight, 1)  
                init.constant_(layer.bias, 0)  
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)  
        self.criterion = CustomMSE()

    def train(self, db2, epochs=10, verbose=True):
        x, y = get_image_data(db2, grid_size=self.grid_size)
        print("Sample 0:\n", x[0], "\n", y[0])
        train_loader, test_loader = self.data_to_loader(x, y)
        self.model = self.training_loop(train_loader, test_loader, verbose=verbose, epochs=epochs)
        return self.model

    def data_to_loader(self, x, y, test_split=0.25):
        assert len(x) == len(y), "x and y must have the same length"
        
        x = torch.from_numpy(x).float()
        y = torch.from_numpy(y).float()

        dataset = utils.TensorDataset(x, y)
        test_size = int(len(dataset) * test_split)
        train_size = len(dataset) - test_size

        overhang = train_size % self.batch_size
        train_size -= overhang
        test_size += overhang

        train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

        print(f"train size: {len(train_dataset)}, test size: {len(test_dataset)}")


        train_loader = utils.DataLoader(train_dataset, batch_size=self.batch_size, drop_last=True, shuffle=True)
        test_loader = utils.DataLoader(test_dataset, batch_size=test_size, drop_last=True, shuffle=False)

        print("Input shape:", train_loader.dataset[0][0].shape)
        print("Output shape:", train_loader.dataset[0][1].shape)

        return train_loader, test_loader

    def training_loop(self, train_loader, test_loader, verbose=True, epochs=50):
        losses = []
        for epoch in range(1, epochs + 1):
            # training
            self.model.train()
            train_loss = 0
            for batch_idx, (data, target) in enumerate(train_loader):
                self.optimizer.zero_grad()
                output = self.model(data)
                loss = self.criterion(output, target)
                loss.backward()
                train_loss += loss.item()
                self.optimizer.step()
            train_loss /= len(train_loader)

            # testing
            self.model.eval()
            test_loss = 0
            with torch.no_grad():
                for i, (data, target) in enumerate(test_loader):
                    output = self.model(data)
                    # print(output.shape, target.shape)
                    test_loss += self.criterion(output, target).item()

            if verbose : print(f'Epoch: {epoch}, Train Loss: {train_loss:.4f} Test Loss: {test_loss:.4f}'); # print(output[0], target[0])
            fig, axs = plt.subplots(3,5, figsize=(10,5))
            # print("sum", target[0].sum())
            print(output[0][0][0][:3][:3])
            for i in range(5):
                axs[0][i].imshow(output[i][0], vmin=0, vmax=1)
                axs[1][i].imshow(target[i][0], vmin=0, vmax=1)
                axs[2][i].imshow(output[i][0] == output[i][0].max().max(), vmin=0, vmax=1)
                axs[0][i].set_title(round(self.criterion(output[i], target[i]).item()*1000,3))
            plt.show()

        return self.model

    def predict_pil(self, pil_images):
        if not isinstance(pil_images, list):
            pil_images = [pil_images]
        preprocessed_images = preprocess_pil(pil_images)
        predictions = self.predict(preprocessed_images)
        print(predictions)
        return predictions

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

def get_image_data(db2, grid_size=16):
    image_paths, positions = db2.get_solved_captchas(count=1000)

    images_raw = []
    positions_raw = []
    for i in range(len(image_paths)):
        try:
            img = Image.open(open(IMAGES_DIR_V2 + image_paths[i], 'rb'))
            img.crop((0,0,0,0))
            images_raw.append(img)
            positions_raw.append(positions[i])
        except Exception as e:
            print(e)
            print(f"Could not load image: {image_paths[i]}")
    print(len(images_raw))
    print(images_raw[0].size)

    useable_indexes = [i for i in range(len(images_raw)) if images_raw[i].size == (500, 536)]

    useable_images = [images_raw[i] for i in useable_indexes]
    positions_raw = [positions_raw[i] for i in useable_indexes]
    print(f"Found {len(useable_images)} useable images")

    return preprocess_pil(useable_images), preprocess_positions(positions_raw, grid_size)

def preprocess_pil(images):
    if not isinstance(images, list):
        images = [images]
    images = [image.crop(CLICKABLE_AREA_BOUNDARIES) for image in images]
    x = np.asarray(images)
    x = x / 255 # norming
    x = np.moveaxis(x, [1,2,3], [2,3,1]) # color channel first
    x = x[:,:-1,:,:] # remove alpha channel
    print(f"x shape: {x.shape}")
    return x

def postprocess_pil(images):
    if len(images.shape) == 3:
        images = np.expand_dims(images, axis=0)
    images *= 255
    images = np.moveaxis(images, [1], [-1]) # color channel last
    images = images.astype(np.uint8)
    return images  

def preprocess_positions(positions, grid_size=16):
    y = np.asarray(positions)
    
    y[:,1] = 1 - y[:,1]

    score = lambda x,y, target_x, target_y: np.e**(-(((x-target_x)**2 + (y-target_y)**2) * 40)**2)
 
    x = np.linspace(0, 1, grid_size)  
    y = np.linspace(0, 1, grid_size)  
    xx, yy = np.meshgrid(x, y)  
    
    coordinates = np.column_stack((xx.ravel(), yy.ravel()))  

    scores = np.array([np.array([
        score(x,y,position[0]/CLICKABLE_AREA_SIZE[0],position[1]/CLICKABLE_AREA_SIZE[1]) 
        for x,y in zip(coordinates[:,0], coordinates[:,1])]).reshape(grid_size, grid_size) for position in positions]
    )

    print("scores shape", scores.shape)
    scores = np.expand_dims(scores, axis=1)
    return scores 
