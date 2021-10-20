# 数据预处理
import logging
import os

import pandas as pd
import torch
import torchvision.utils
from torchvision import transforms
import matplotlib.pyplot as plt
from PIL import Image
from torch.utils.data import dataset,dataloader
import config
from logger import  logger,init_log


class CaptchaDataset(dataset.Dataset):
    """
    ## 加载数据，数据格式为
    # train: label.png
    # test: index.png
    """

    def __init__(self, root,multi = False, transformer = None,train = True):
        """
        captcha dataset
        :param root: the paths of dataset, 数据类型为 root/label.png ...
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
        self.labels = None
        if self.train:
            if multi:
                paths = [os.path.join(self.root,path) for path in os.listdir(self.root)]
            else:
                paths = [self.root]
            self._extract_images(paths)
        else:
            paths = os.listdir(self.root)
            self.image_paths = []
            for path in paths:
                if path.endswith(".png") or path.endswith(".jpg") or path.endswith("jpeg"):
                    self.image_paths.append(os.path.join(self.root,path))
        assert self.image_paths

    def _extract_images(self, paths):
        image_paths = []
        labels = []
        logger.info(f'read data from {paths}')
        for item_path in paths:
            logger.info(f'read data from {item_path}')
            info = pd.read_json(os.path.join(item_path,'train_label.json',),dtype=str)
            item_image_paths = [os.path.join(item_path,path) for path in list(info['ID'].values)]
            item_labels = list(info['label'].values)
            image_paths += item_image_paths
            labels += item_labels
        self.image_paths = image_paths
        self.labels = labels
        assert len(self.image_paths) == len(self.labels)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        fail = False
        try:
            img = Image.open(image_path)
            img = img.convert("RGB")
        except Exception as e:
            logger.error(e)
            img = Image.open('2-mc5m.png')
            img = img.convert("RGB")
            fail = True
        if self.train:
            if fail:
                label = 'mc5m'
            else:
                label = str(self.labels[idx])
                label = label.lower()
            target = [config.CHAR2LABEL[c] for c in label]
            target_length = [len(target)]
            target = torch.LongTensor(target)
            target_length = torch.LongTensor(target_length)
            img = self.transformer(img)
            return img, target, target_length
        else:
            return image_path, self.transformer(img)

def captcha_collate_fn(batch):

    images, targets, target_lengths = zip(*batch)
    images = torch.stack(images, 0)
    targets = torch.cat(targets, 0)
    target_lengths = torch.cat(target_lengths, 0)
    return images, targets, target_lengths

def train_loader(train_path,multi = False,train_rate = config.train_rate,batch_size = config.batch_size,
                 height = config.height, width = config.width,collate_fn = captcha_collate_fn,
                 transformer = None):
    """
    
    :param train_path:  the path of training data
    :param batch_size: 
    :param height resize height
    :param width: resize width
    :return: 
    """""
    if transformer is None:
        transformer = transforms.Compose(
            [
              #transforms.RandomAffine((0.9,1.1)),
              #transforms.RandomRotation(8),
              transforms.Resize((height, width)),
              transforms.ToTensor(),
              transforms.Normalize(mean=config.mean,std= config.std)
             ]
        )
    train_set = CaptchaDataset(train_path,multi = multi, transformer=transformer)
    train_len = int(len(train_set)*train_rate)
    train_data, val_data = torch.utils.data.random_split(train_set,[train_len,len(train_set)-train_len])
    return dataloader.DataLoader(train_data, batch_size=batch_size, shuffle=True,collate_fn= collate_fn),\
           dataloader.DataLoader(val_data, batch_size=batch_size, shuffle=True,collate_fn= collate_fn)


def test_loader(test_path,batch_size = config.test_batch_size, height = config.height,
                width = config.width,transformer = None):
    """

    :param test_path:
    :param batch_size:
    :param x: resize
    :param y:
    :return:
    """
    if transformer is None:
        transformer = transforms.Compose(
        [transforms.Resize((height, width)),
         transforms.ToTensor(),
         transforms.Normalize(mean=config.mean, std=config.std)
         ]
    )
    test_set = CaptchaDataset(test_path,train = False, transformer=transformer)
    return dataloader.DataLoader(test_set, batch_size=batch_size, shuffle=False)



if __name__ == '__main__':
     init_log('test')
     height,width = 32,100
     transformer = transforms.Compose(
        [
            #transforms.RandomAffine((0.9, 1.1)),
            #transforms.RandomRotation(8),
            transforms.Resize((height, width)),
            transforms.ToTensor(),
        ]
     )
     path = '/Users/sjhuang/Documents/docs/dataset/train'
     train_loader,val_loader = train_loader(path,multi = True,transformer = transformer)
     imgs, targets, target_lens  = next(iter(train_loader))
     grid_img = torchvision.utils.make_grid(imgs,nrow = 4)
     plt.imshow(grid_img.permute(1, 2, 0))
     plt.imsave(f"pres/preprocessed_{height}_{width}.jpg",grid_img.permute(1, 2, 0).numpy())
     # num = 0
     # for imgs, targets, target_lens  in train_loader:
     #     num += len(imgs)
     #     logger.info(f"imgs:{imgs.shape}, {num}")



