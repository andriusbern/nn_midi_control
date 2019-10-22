import pyaudio
import numpy as np
import time
import sys
import scipy
import wave, mido

from ml_midi.config import audio_config
from ml_midi.config import ConfigManager as config

class AudioIO(object):
    def __init__(
        self, 
        channels=1, 
        chunk_size=2048, 
        sample_rate=44100, 
        device_index=1):

        self.format = pyaudio.paInt16
        self.channels = channels
        self.sample_rate = sample_rate
        self.samples_per_chunk = chunk_size
        self.device_index = device_index
        self.volume = 10
        self.n_chunks = 32

        self.current_chunk = 0
        self.current_sample = None
        self.chunks = None

        self.looping = False
        self.playing_all = False
        self.playing = False
        self.monitoring = False
        self.recording = False

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
            output_device_index=0,
            channels = self.channels,
            output = True)
        self.output.start_stream()

    def record(self, n_samples):
        """
        Record n_samples
        """
        size = self.samples_per_chunk if n_samples is None else n_samples
        raw = self.input.read(num_frames=size, exception_on_overflow=False)
        data = np.fromstring(raw, dtype=np.int16)

        return data, raw

    def playback(self, wave):
        wave /= volume/100
        self.output.write(wave)
        # self.output.stop_stream()

    def get_device_info(self):
        info = self.instance.get_host_api_info_by_index(0)
        m, list = '', []
        for i in range(info.get('deviceCount')):
            if (self.instance.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                info = self.instance.get_device_info_by_host_api_device_index(0, i).get('name')
                m += 'Input Device id: {}, {}\n'.format(i,info)
                list += [info]
                
        return m, list

    def pause(self):
        self.input.stop_stream()

    def play_sample(self, status):
        if status:
            print('play')
            sample = self.main_widget.sample_widget.current_sample
            print(sample.wave)
            # self.audio.playback(sample.wave)

        else:
            print('pause')

    def loop(self, val):
        self.looping = val
        print('loop',val)

    def play_chunk(self):
        if self.playing:
            # scaled = self.current_sample.wave * self.volume / 100
            scaled = self.chunks[self.current_chunk] * self.volume / 100
            scaled = scaled.astype(np.uint16)
            self.output.write(scaled)
            self.current_chunk += 1
            if self.current_chunk >= self.n_chunks - 1:
                self.current_chunk = 0
                # print(self.looping, self.playing_all)
                if not self.looping:
                    self.playing = False
                    self.manage_buttons()
                if self.playing_all:
                    self.get_next_sample()
                    
            self.seek(self.current_chunk)
            
                
    def new_sample(self, sample):
        """
        Update the sample globally?
        """
        self.current_sample = sample
        print(self.current_sample.wave)
        self.chunks = np.split(self.current_sample.wave, self.n_chunks, axis=0)
        self.current_chunk = 0
        self.display_update()

    def play_all(self):
        print('playall')

    def pause(self):
        print('pause')
    
    def stop(self):
        print('stop')

    def new_label(self):
        print('lab')

    def monitor(self):
        # if status: print('Mon')
        # else: print('Mon Stopped')
            # def detect(self):
        data, _ = self.record(config.DETECTION_SAMPLE_SIZE)
        self.display_update(data, all=False)
        self.current_max = max(data)
        if self.recording and self.current_max > config.THRESHOLD:
            self.record_sample()
            

    def close(self):
        self.input.stop_stream()
        self.input.close()
        self.instance.terminate()

    def seek(self):
        pass

    def get_next_sample(self):
        pass

    def display_update(self):
        pass

    def manage_buttons(self):
        pass


if __name__ == "__main__":
    p = AudioIO(**audio_config)
    for _ in range(10):
        samples_per_chunk = p.get_chunk()
    p.data_output(samples_per_chunk)