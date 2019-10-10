import os, sys

MAIN_DIR = os.path.dirname(os.path.realpath(__file__))
DATA = os.path.join(MAIN_DIR, 'data')

SAMPLE_RATE = 44100
RECORDING_LENGTH = 4096 # 16384 #8192 # 2048 # 4096
SPECTROGRAM_LOW  = 20
SPECTROGRAM_HIGH = 20000
FREQUENCY_BANDS  = 100
TIMESTEPS = 100
FFT_LENGTH = 2048
THRESHOLD = 100
NORMALIZE = False
DETECTION_SAMPLE_SIZE = 128

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

class ParameterContainer(dict):
    def __getattribute__(self, item):
        return self[item]

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

