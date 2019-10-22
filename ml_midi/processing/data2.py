import numpy as np
import time, datetime, os, sys
import cv2, scipy, wave
from PIL import Image
import ml_midi.processing.process as ap
import glob

from ml_midi.config import ConfigManager as config

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
        self.spectrogram = None
        # self.spectrogram = self.create_spectrogram()

    def create_spectrogram(self):
        spec = self.spectrogram = ap.melspectrogram(self.wave)
        return spec

    def from_wave(self, wave, label, dataset):
        self.wave = wave
        self.raw = None #!
        self.spectrogram = None
        self.label = label

        return self

class Label(object):
    def __init__(self, name, samples=[], params={}):
        self.name = ''
        self.type = None
        self.params = params
    
    def to_dict(self):

        return 

class Output(object):
    def __init__(self, type):
        pass



class Dataset(object):
    """
    Construct either from a folder or a list of wav files + labels
    """
    def __init__(self, name, existing=False):

        self.name = name
        self.IO = DataIO()
        self.hashmap, self.samples_per_label = {}, {}
        self.labels = []
        self.samples = []
        self.current_sample_id = 0

        self.image_dir = os.path.join(config.DATA, 'images',name)
        self.audio_dir = os.path.join(config.DATA, 'audio', name)

        if existing:
            self.load_existing()
        else:
            self.create_new()
        print(self.samples_per_label)

    def create_new(self, name):
        self.name = name
        self.labels, self.samples = ['default'], []
        self.hashmap, self.samples_per_label = {}, {}

        self.image_dir = os.path.join(config.IMAGES, name)
        self.audio_dir = os.path.join(config.AUDIO, name)

        self.current_label = 'default'
        os.makedirs(os.path.join(self.audio_dir, 'default'))

        self.current_sample_id = 0

        self.n_labels = len(np.unique(self.labels))

    def get_sample(self, sample_no):
        try:
            return self.hashmap[self.current_label][sample_no]
        except Exception as e:
            print(e)
        
    def remove_sample(self, sample_no):
        try:
            self.hashmap[self.current_label].remove(sample_no)
        except Exception as e:
            print(e)

    def new_label(self, name):
        self.labels.append(name)
        self.hashmap[name] = []
        self.samples_per_label[name] = 0
        self.current_label = name
        os.makedirs(os.path.join(self.audio_dir, name))
            
    def new_sample(self, wave, bytestring=None, label=None, save=False):
        """
        """
        new_sample = DataSample(wave=wave, raw=bytestring, label=label)

        if label is None:
            label = self.current_label
        if label in self.hashmap.keys():
            self.hashmap[label].append(new_sample)
            self.samples_per_label[label] += 1
        else:
            self.hashmap[label] = [new_sample]
            self.samples_per_label[label] = 1

        new_sample.id = sid = self.samples_per_label[label]
        self.samples.append(new_sample)
        # self.labels.append(label)

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

    def load_existing(self):
        
        subdirs = [x[0] for x in os.walk(self.audio_dir)][1:]
        self.current_label = 'default'
        self.hashmap, self.samples_per_label = {}, {}
        self.labels = [x.split('/')[-1] for x in subdirs]
        print(self.labels)

        for i, subdir in enumerate(subdirs):
            print(self.labels[i])
            waves = self.IO.read_wav_directory(subdir)
            for wave in waves:
                sample = self.new_sample(wave=wave, label=self.labels[i])
        self.labels.sort()


    def write_image_dataset(self):
        """
        Writes an image dataset of current samples,
        Using the current config
        """
        # Save the conf file somehow
        dataset_folder = path = os.path.join(self.audio_dir, label)

        for sample in self.samples:

            samples_folder = os.path.join(dataset_folder, sample.label)
            if not os.path.isdir(samples_folder):
                os.makedirs(samples_folder)

            path = os.path.join(samples_folder, sample.id+'.png')
            image = sample.create_spectrogram()
            self.IO.write_grayscale(path=path, image=image)

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

    def summary(self, print=False):
        msg = 'Dataset: "{}", n: {}\n'.format(self.name, len(self.samples))
        msg += '\nCategories   | samples:\n'
        for key in self.hashmap.keys():
            msg += '   {:10}: {}\n'.format(key, len(self.hashmap[key]))
        
        return msg

class DataIO(object):
    def __init__(self):
        # self.data_dir = config.DATA
        # self.sample_nr = 0
        # self.dataset = Dataset()
        pass

    def write_wav(self, path, bytestring, nchannels=1):
    
        wavefile = wave.open(path, 'wb')
        wavefile.setnchannels(nchannels)
        wavefile.setsampwidth(2)
        wavefile.setframerate(config.SAMPLE_RATE)
        wavefile.writeframes(bytestring)
        

    def read_wav(self, path):
        """
        Returns a numpy array of the wav file
        """
        f = wave.open(path, 'rb')
        data = f.readframes(4096)
        print(f.getparams())
        data = np.fromstring(data, dtype=np.int16)
        # fs, data = scipy.io.wavfile.read(path)
        # print(data)
        return data

    def read_wav_directory(self, dir_path):
        """
        Returns a list of np arrays of wav files
        """
        files = glob.glob(dir_path+"/*.wav")
        waves = []
        for f in files:
            filepath = os.path.join(dir_path, f)
            waves.append(self.read_wav(path=filepath))

        return waves

    @staticmethod
    def read_image(self):
        pass

    def write_grayscale(self, path, image):
        image = Image.fromarray(image).convert('L')
        image = image.transpose(Image.ROTATE_90)
        print('Writing image sample to: {} \n'.format(location))
        image.save(path)

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

    def one_hot_label(self, label, n_labels):
        label = np.zeros([1, n_labels])
        return label

