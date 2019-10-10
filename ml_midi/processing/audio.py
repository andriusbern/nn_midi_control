import pyaudio
import numpy as np
import time
import sys
import scipy
import wave, mido

from ml_midi.config import audio_config

class AudioIO():
    def __init__(self, channels=1, chunk_size=2048, 
                 sample_rate=44100, device_index=1):

        self.format = pyaudio.paInt16
        self.channels = channels
        self.sample_rate = sample_rate
        self.samples_per_chunk = chunk_size
        self.device_index = device_index
        self.detection_buffer_size = 256

        self.instance = pyaudio.PyAudio() # create pyaudio instantiation
        print(self.instance.get_sample_size(self.format))
        self.input = self.instance.open(
            format = self.format, 
            rate = self.sample_rate,
            channels = self.channels,
            input_device_index = self.device_index,
            input = True,
            frames_per_buffer=self.samples_per_chunk)

        self.output = self.instance.open(
            format = self.format, 
            rate = self.sample_rate,
            channels = self.channels,
            output = True)

    def record(self, n_samples):
        """
        Record n_samples
        """
        size = self.samples_per_chunk if n_samples is None else n_samples
        raw = self.input.read(num_frames=size, exception_on_overflow=False)
        data = np.fromstring(raw, dtype=np.int16)

        return data, raw
    
    def playback(self, wave):
        self.output.start_stream()
        self.output.write(wave)
        self.output.stop_stream()

    def get_device_info(self):
        info = self.instance.get_host_api_info_by_index(0)
        for i in range(info.get('deviceCount')):
            if (self.instance.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", self.instance.get_device_info_by_host_api_device_index(0, i).get('name'))

    def start_recording(self):
        self.input.start_stream()

    def pause(self):
        self.input.stop_stream()

    def close(self):
        self.input.stop_stream()
        self.input.close()
        self.instance.terminate()

if __name__ == "__main__":
    p = AudioIO(**audio_config)
    for _ in range(10):
        samples_per_chunk = p.get_chunk()
    p.data_output(samples_per_chunk)