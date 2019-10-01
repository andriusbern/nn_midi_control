import pyaudio
import numpy as np
import time
import sys
import scipy.fftpack
from config import audio_config

# pyaudio.
class pyaudioWrapper():
    def __init__(self, channels=1, chunk_size=2048, sample_rate=44100, device_index=1):

        self.format = pyaudio.paInt16
        self.channels = channels
        self.sample_rate = sample_rate
        self.chunk = chunk_size
        self.device_index = device_index
        self.chunk_length = self.chunk / self.channels
        self.detection_buffer_size = 256

        self.instance = pyaudio.PyAudio() # create pyaudio instantiation
        self.stream = self.instance.open(format = self.format, 
                                         rate = self.sample_rate,
                                         channels = self.channels,
                                         input_device_index = self.device_index,
                                         input = True,
                                         frames_per_buffer=self.chunk)
        self.start()

    def start(self):
        self.stream.start_stream()

    def triggered(self, threshold):
        data = np.fromstring(self.stream.read(self.detection_buffer_size, exception_on_overflow=False),dtype=np.int16)
        high = np.max(data)
        print(high)
        if high > threshold:
            return True
        return False        

    def spectrogram(self):
        chunks = 50
        bins = 20
        spectrogram = np.zeros([chunks, bins])
        for i in range(chunks):
            data = np.fromstring(self.stream.read(256, exception_on_overflow=False),dtype=np.int16)
            fft = self.fft(data)
            fft = [np.mean(fft[x:(x+1)*bins]) for x in range(bins)]
            spectrogram[i, :] = fft
        
        return spectrogram

    def get_chunk(self, size=None):
        if size is None:
            size = self.chunk
        data = np.fromstring(self.stream.read(size, exception_on_overflow=False),dtype=np.int16)
        # self.stream.stop_stream()
        # print(np.max(data))
        return data

    def data_output(self, data):
        data = np.reshape(data, (self.chunk, self.channels))
        for i in range (len(data)):
            for j in range (self.channels):
                sys.stdout.write('\nChannel: {}, sample {}:  |  {} '.format(j+1, i+1, data[i][j]))

    def fft(self, data, bins=None):
        fft = scipy.fftpack.fft(data)
        fft = np.array(fft[:len(data)//8], dtype=np.float32)
        fft = [abs(x) for x in fft]
        if bins is not None:
            fft = [np.mean(fft[x:(x+1)*bins]) for x in range(bins)]
        return fft

    def get_device_info(self):
        info = self.instance.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (self.instance.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", self.instance.get_device_info_by_host_api_device_index(0, i).get('name'))

if __name__ == "__main__":
    p = pyaudioWrapper(**audio_config)
    for _ in range(10):
        chunk = p.get_chunk()
    p.data_output(chunk)