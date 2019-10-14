import os, sys
import numpy as np

# Directories
SRC_DIR = os.path.dirname(os.path.realpath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SRC_DIR, os.pardir))
DATA = os.path.join(SRC_DIR, 'data')
ICONS = os.path.join(MAIN_DIR, 'icons')

SAMPLE_RATE = 44100
RECORDING_LENGTH = 4096 # 16384 #8192 # 2048 # 4096
THRESHOLD = 100
DETECTION_SAMPLE_SIZE = 128

# Spectrograms
SPECTROGRAM_LOW  = 20
SPECTROGRAM_HIGH = 20000
FREQUENCY_BANDS  = 100
TIMESTEPS = 100
FFT_LENGTH = 2048
NORMALIZE = False

class ConfigManager():

    # Directories
    SRC_DIR = os.path.dirname(os.path.realpath(__file__))
    MAIN_DIR = os.path.abspath(os.path.join(SRC_DIR, os.pardir))
    DATA = os.path.join(SRC_DIR, 'data')
    ICONS = os.path.join(MAIN_DIR, 'icons')
    AUDIO = os.path.join(DATA, 'audio')
    IMAGES = os.path.join(DATA, 'images')
    MODELS = os.path.join(SRC_DIR, 'models')

    ############
    # Parameters
    ############
    # Audio
    SAMPLE_RATE = 44100
    RECORDING_LENGTH = 4096 # 16384 #8192 # 2048 # 4096
    THRESHOLD = 100
    DETECTION_SAMPLE_SIZE = 128

    # Spectrograms
    SPECTROGRAM_LOW  = 20
    SPECTROGRAM_HIGH = 20000
    FREQUENCY_BANDS  = 100
    TIMESTEPS = 100
    FFT_LENGTH = 1024
    NORMALIZE = False


    audio_config = dict(
        channels=1,
        device_index=1,
        chunk_size=128,
        sample_rate=SAMPLE_RATE)

    # Value ranges
    ranges = dict(
        RECORDING_LENGTH = [2**x for x in range(6, 19)],
        THRESHOLD = [x*10 for x in range(5001)],
        DETECTION_SAMPLE_SIZE = [2**x for x in range(4, 10)],

        # Spectrogram
        SPECTROGRAM_LOW  = np.geomspace(20, 20000, 50, dtype=np.uint16),
        SPECTROGRAM_HIGH = np.geomspace(20, 20000, 50, dtype=np.uint16),
        FREQUENCY_BANDS  = [x for x in range(10, 201)],
        TIMESTEPS = [x for x in range(10, 201)],
        FFT_LENGTH = [2**x for x in range(5, 14)])

    @staticmethod
    def get(parameter):
        return ConfigManager.__dict__[parameter] 
       
    def set(parameter, value):
        ConfigManager.__dict__[parameter] = value
        # setattr(locals(), parameter, value)
        # setattr(globals(), parameter, value)

    def __init__(self):
        pass
    
    def get_defaults(self):
        pass

    def write_config(self, path):
        pass

    def read_config(self, path):
        pass

    @staticmethod
    def translate(parameter):
        translate = dict(
            RECORDING_LENGTH = 'Recording Length',
            THRESHOLD = 'Threshold',
            DETECTION_SAMPLE_SIZE = 'Detection Sample Size',

            # Spectrogram
            SPECTROGRAM_LOW  = 'Min Frequency',
            SPECTROGRAM_HIGH = 'Max Frequency',
            FREQUENCY_BANDS  = 'Spectrogram Height',
            TIMESTEPS = 'Spectrogram Width',
            FFT_LENGTH = 'FFT Length')

        return translate[parameter]



audio_config = dict(
    channels=1,
    device_index=0,
    chunk_size=128,
    sample_rate=SAMPLE_RATE)

net_config = dict(
    filters=[16, 32, 64],
    kernel_size=[3, 3, 3],
    strides=[1, 1, 1],
    fc_layers=[128, 64, 32],
    epochs=10)

interface_config = dict(
    total_length = RECORDING_LENGTH,
    display_sample_size = 128,
    scale_fft=True,
    log_scale_fft=True)

spectrogram_config = dict(
    nperseg=FFT_LENGTH)

melspectrogram = dict(
    n_fft=FFT_LENGTH,
    sr=SAMPLE_RATE,
    power=1.0)

mod_config = dict(
    SAMPLE_RATE = SAMPLE_RATE,
    RECORDING_LENGTH = RECORDING_LENGTH, # 16384 #8192 # 2048 # 4096
    SPECTROGRAM_LOW  = SPECTROGRAM_LOW,
    SPECTROGRAM_HIGH = SPECTROGRAM_HIGH,
    FREQUENCY_BANDS  = FREQUENCY_BANDS,
    TIMESTEPS = TIMESTEPS,
    FFT_LENGTH = FFT_LENGTH,
    THRESHOLD = THRESHOLD, 
    NORMALIZE = NORMALIZE,
    DETECTION_SAMPLE_SIZE = DETECTION_SAMPLE_SIZE
)

recording_config = dict(
    SAMPLE_RATE = SAMPLE_RATE,
    RECORDING_LENGTH = RECORDING_LENGTH, # 16384 #8192 # 2048 # 4096
    THRESHOLD = THRESHOLD, 
    DETECTION_SAMPLE_SIZE = DETECTION_SAMPLE_SIZE
)

spec_config = dict(
    SPECTROGRAM_LOW  = SPECTROGRAM_LOW,
    SPECTROGRAM_HIGH = SPECTROGRAM_HIGH,
    FREQUENCY_BANDS  = FREQUENCY_BANDS,
    TIMESTEPS = TIMESTEPS,
    FFT_LENGTH = FFT_LENGTH,
    NORMALIZE = NORMALIZE,
)

mappings = dict(
    SPECTROGRAM_LOW  = SPECTROGRAM_LOW,
    SPECTROGRAM_HIGH = SPECTROGRAM_HIGH,
    FREQUENCY_BANDS  = FREQUENCY_BANDS,
    TIMESTEPS = TIMESTEPS,
    FFT_LENGTH = FFT_LENGTH,
    NORMALIZE = NORMALIZE,
    SAMPLE_RATE = SAMPLE_RATE,
    RECORDING_LENGTH = RECORDING_LENGTH, # 16384 #8192 # 2048 # 4096
    THRESHOLD = THRESHOLD, 
    DETECTION_SAMPLE_SIZE = DETECTION_SAMPLE_SIZE
)