import numpy as np
import time, datetime, os, sys
import config
from PIL import Image
import cv2

class DataHandler(object):
    def __init__(self):
        self.data_dir = config.DATA

    def write_image(self, image, dataset, label):
        timestamp = datetime.datetime.now().strftime('%m-%d_%H:%M:%S')
        image = Image.fromarray(image).convert('L')
        directory = os.path.join(self.data_dir, dataset, label)
        if not os.path.isdir(directory): os.makedirs(directory)
        location = os.path.join(directory, timestamp) + '.png'
        print('\n'+location)
        image.save(location)

    def load_dataset(self, dataset):
        data, labels = [], []
        folder_path = os.path.join(self.data_dir, dataset)
        folders = os.listdir(folder_path)
        for folder in folders:
            sample_path = os.path.join(folder_path, folder)
            images = os.listdir(sample_path)
            for image in images:
                path = os.path.join(sample_path, image)
                data.append(Image.open(path))
                label = int(folder)
                labels.append(label)
        data = np.stack(data, axis=0)

        return data, np.array(labels)

    def split_data(self):
        """
        Split into train/test sets
        """

    def one_hot_label(self, label, n_labels):
        label = np.zeros([1, n_labels])
            
        return label

    def get_batch(self):
        return 0, 0
        
    def preprocess(self):
        pass

class Dataset(object):
    def __init__(self, name):
        self.name = name
        self.samples, self.labels = DataHandler().load_dataset(name)
        self.hashmap = {}
        self.h, self.w, self.n_samples = self.samples.shape
        self.n_labels = len(np.unique(self.labels))
        self.split_data()
        self.summary()

    def split_data(self):
        """
        Splits the data into train/test sets
        """
        self.train_set = None
        self.train_labels = None
        self.test_set = None
        self.test_labels = None

    def get_batch(self):
        return 0, 0

    def visualize(self):
        w_name = 'Sample Display'
        cv2.namedWindow(w_name)
        cv2.resizeWindow(w_name, 600, 600)
        for sample in self.samples:
            cv2.imshow(w_name, sample)
            cv2.waitKey(200)
        cv2.destroyWindow(w_name)

    def summary(self):
        print('Loaded {} dataset: \n  Samples: {}, categories: {}'.format(self.name, len(self.labels), self.n_labels))