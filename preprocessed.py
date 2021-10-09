# 数据预处理
import os
import torch
import cv2
import torchvision.utils
from torchvision import transforms
import matplotlib.pyplot as plt
from PIL import Image
from torch.utils.data import dataset,dataloader
## 加载数据，数据格式为
# train: label.png
# test: index.png
import config

class CaptchaDataset(dataset.Dataset):
    def __init__(self, root, transformer = None,train = True):
        """
        captcha dataset
        :param root: the path of dataset, 数据类型为 root/label.png ...
        :param transformer: transformer for image
        :param train: train of not
        """
        super(CaptchaDataset, self).__init__()
        assert root
        self.root = root
        self.train = train
        if transformer:
            self.transformer = transformer
        else:
            self.transformer = transforms.ToTensor()
        self.image_paths = os.listdir(self.root)
        assert self.image_paths
        self.labels = None
        if self.train:
            self.labels = [image_path.split('.')[0] for image_path in self.image_paths]

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = os.path.join(self.root,self.image_paths[idx])
        label = self.labels[idx]
        img = Image.open(image_path)
        img = img.convert("RGB")
        return self.transformer(img), label

def train_loader(train_path,batch_size,x = config.x, y = config.y):
    """
    
    :param train_path: 
    :param batch_size: 
    :param x: 
    :param y: 
    :return: 
    """""
    transformer = transforms.Compose(
        [transforms.Resize((x, y)),
         transforms.ToTensor(),
         ]
    )
    train_set = CaptchaDataset(train_path, transformer=transformer)
    return dataloader.DataLoader(train_set, batch_size=batch_size, shuffle=True)


def test_loader(test_path,batch_size, x = config.x, y = config.y):
    """

    :param test_path:
    :param batch_size:
    :param x:
    :param y:
    :return:
    """
    transformer = transforms.Compose(
        [transforms.Resize((x, y)),
         transforms.ToTensor(),
         ]
    )
    test_set = CaptchaDataset(test_path,train = False, transformer=transformer)
    return dataloader.DataLoader(test_set, batch_size=batch_size, shuffle=False)



if __name__ == '__main__':

     x = 30
     y = 90
     transformer = transforms.Compose(
         [transforms.Resize((x,y)),
          transforms.ToTensor(),
          ]
     )
     train_set = CaptchaDataset(config.train_data_path,transformer=transformer)
     train_loader = dataloader.DataLoader(train_set,batch_size=64,shuffle=False)

     imgs, labels = next(iter(train_loader))
     grid_img = torchvision.utils.make_grid(imgs,nrow = 4)
     print(grid_img.shape)
     plt.imshow(grid_img.permute(1, 2, 0))
     plt.imsave(f"pres/preprocessed_{x}_{y}.jpg",grid_img.permute(1, 2, 0).numpy())

