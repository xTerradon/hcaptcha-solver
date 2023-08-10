import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as utils

import PIL

IMAGE_DIR = "./src/images/"

class Training:
    def __init__(self):
        self.batch_size = 16
        self.test_batch_size = 1000
        self.epochs = 20
        self.lr = 0.00001
        self.log_interval = 1

        self.model = nn.Sequential(
            nn.Conv2d(3, 20, kernel_size=5),
            nn.ReLU(),
            nn.MaxPool2d(2, stride=2),
            nn.Conv2d(20, 10, kernel_size=5),
            nn.ReLU(),
            nn.MaxPool2d(2, stride=2),
            nn.Flatten(),
            nn.Linear(8410,64),
            nn.ReLU(),
            nn.Linear(64,1),
            nn.Sigmoid()
        )

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.criterion = nn.BCELoss()

    def train(self, train_loader, test_loader):
        for epoch in range(1, self.epochs + 1):
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
            
            test_loss /= len(test_loader.dataset)
            print(output[0])
            print(f'Epoch: {epoch}, Test set: Average loss: {test_loss:.4f}, Accuracy: {correct}/{len(test_loader.dataset)}, {100. * correct / len(test_loader.dataset):.0f}%')
            

def data_to_loader(x, y, test_split=0.25, batch_size=16):
    x_train = torch.from_numpy(x).float()
    y_train = torch.from_numpy(y).float()

    dataset = utils.TensorDataset(x_train, y_train)
    train_size = int((1 - test_split) * len(dataset))
    test_size = len(dataset) - train_size
    print(f"train size: {train_size}, test size: {test_size}")
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    train_loader = utils.DataLoader(train_dataset, batch_size=batch_size, drop_last=True)
    test_loader = utils.DataLoader(test_dataset, batch_size=batch_size, drop_last=True)

    print("single element shape:", train_loader.dataset[0][0].shape)

    return train_loader, test_loader

    
def train_model_on_captcha_string(db_handler, captcha_string=None, batch_size=16):
    if captcha_string is None:
        captcha_string = db_handler.get_most_solved_captcha_string()
    print(f'Training model on {captcha_string}...')
    data = db_handler.get_solved_data(captcha_string, 1000)
    x = np.asarray([np.asarray(PIL.Image.open(open(IMAGE_DIR+path, 'rb'))) for path in data["path"]])
    x = np.moveaxis(x, [1,2,3], [2,3,1]) # color channel first
    y = data["category"].values.reshape(-1,1)
    print(f"x shape: {x.shape}")
    print(f"y shape: {y.shape}")

    train_loader, test_loader = data_to_loader(x, y)

    training = Training()
    training.train(train_loader, test_loader)

    
    