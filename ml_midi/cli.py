import sys, random, os, time
import numpy as np
from ml_midi.processing import AudioIO, Dataset, DataSample, Midi
from ml_midi.learning import RetardedClassifier
import ml_midi.config as config

class CLI(object):
    def __init__(self, **kwargs):
        
        self.audio = AudioIO(**config.audio_config) 
        self.midi = Midi()
        self.classifier = RetardedClassifier()

        self.threshold = 5000
        self.recording = False
        self.detection_buffer = config.interface_config['display_sample_size']
        self.spectrogram = np.zeros([config.FREQUENCY_BANDS, config.TIMESTEPS])

        # Data
        self.label = '0'
        self.dataset = 'new'
        self.data_handler = DataIO()

    def detect(self):
        if self.recording:
            self.record_sample()
            self.recording = False
        else:
            data = self.audio.record(self.detection_buffer)
            if max(data) > self.threshold:
                self.recording = True
        
    def record_sample(self):
        t0 = time.time()
        data = self.audio.record(config.RECORDING_LENGTH)
        sample = DataSample(wave=data)
        spectrogram = np.flip(sample.spectrogram.T)[::-1]
        y = self.classifier.classify(spectrogram)
        self.midi.send_midi(msg_id=y)
        print(y, time.time() - t0)
    
    def main(self):
        print('CLI interface. CTRL+C to exit.')
        try:
            while True:
                self.detect()
        except KeyboardInterrupt:
            print('Exit.')

if __name__ == "__main__":

    interface = CLI()
    interface.main()