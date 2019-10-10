import numpy as np
import time, datetime, os, sys
import ml_midi.config as config
import cv2, scipy, wave
from PIL import Image
import ml_midi.processing.process as ap


class DataSample(object):
    def __init__(self, filename=None, wave=None, raw=None, label=None):
        assert(filename is not None or wave is not None, 
               'Must pass a either a wave array or a valid filename.')

        if filename is None:
            self.wave = wave
            self.label = label
        if wave is None:
            self.wave, self.label = self.load_from_file(filename)

        self.raw = raw
        self.id = ''
        self.spectrogram = ap.melspectrogram(self.wave)

    def from_wave(self, wave, label, dataset):
        self.wave = wave
        self.raw = None #!
        self.spectrogram = None
        self.label = label

        return self


class Dataset(object):
    """
    Construct either from a folder or a list of wav files + labels
    """
    def __init__(self, name, existing=False):
        self.name = name
        self.labels, self.samples = [], []
        self.hashmap = {}

        self.image_dir = os.path.join(config.DATA, 'images',name)
        self.audio_dir = os.path.join(config.DATA, 'audio', name)

        self.current_sample_id = 0
        self.n_labels = len(np.unique(self.labels))
        self.IO = DataIO()

    def new_sample(self, wave, bytestring, label=None, save=False):
        """
        """
        new_sample = DataSample(wave=wave, raw=bytestring, label=label)
        new_sample.id = sid = self.current_sample_id
        self.samples.append(new_sample)
        self.labels.append(label)

        if label is not None:
            if label in self.hashmap.keys():
                self.hashmap[label].append(new_sample)
            else:
                self.hashmap[label] = [new_sample]

        if save:
            folder = path = os.path.join(self.audio_dir, label)
            if not os.path.isdir(folder):
                os.makedirs(folder)

            path = os.path.join(folder, str(sid)+'.wav')
            self.IO.write_wav(
                path=path, 
                bytestring=bytestring)
        self.current_sample_id += 1

        return new_sample

    def write_image_dataset(self):
        """
        Writes an image dataset of current samples,
        Using the current config
        """
        # Save the conf file somehow


    def split_data(self):
        """
        Splits the data into train/test sets
        """
        self.train_set = None
        self.train_labels = None
        self.test_set = None
        self.test_labels = None

    def visualize(self, audio_engine):
        w_name = 'Sample Display'
        cv2.namedWindow(w_name)
        cv2.resizeWindow(w_name, 600, 600)
        for sample in self.samples:
            cv2.imshow(w_name, sample.spectrogram)
            audio_engine.playback(sample.raw)
            cv2.waitKey(200)
        cv2.destroyWindow(w_name)

    def load_image_dataset(self, dataset):
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

    def summary(self):
        print('Loaded {} dataset: \n  Samples: {}, categories: {}'.format(self.name, len(self.labels), self.n_labels))



class DataIO(object):
    def __init__(self):
        # self.data_dir = config.DATA
        # self.sample_nr = 0
        # self.dataset = Dataset()
        pass

    @staticmethod
    def write_wav(path, bytestring, nchannels=1):
    
        wavefile = wave.open(path, 'wb')
        wavefile.setnchannels(nchannels)
        wavefile.setsampwidth(2)
        wavefile.setframerate(config.SAMPLE_RATE)
        wavefile.writeframes(bytestring)

    @staticmethod
    def read_wav(self):
        pass

    @staticmethod
    def read_image(self):
        pass

    @staticmethod
    def write_image(self):
        pass

    @staticmethod
    def write_image(self, image, dataset, label):
        timestamp = datetime.datetime.now().strftime('%m-%d_%H:%M:%S')
        image = Image.fromarray(image).convert('L')
        directory = os.path.join(self.data_dir, dataset, label)
        if not os.path.isdir(directory): os.makedirs(directory)
        location = os.path.join(directory, timestamp) + '.png'
        print('\n'+location)
        image = image.transpose(Image.ROTATE_90)
        image.save(location)

    def write_wave(self, wave):
        pass

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
