import numpy as np
import scipy
import librosa
import math
from ml_midi.config import ConfigManager as config


def spectrogram_manual(wave, bins):
    """
    """
    logscale = np.logspace(0, 10, config.FREQUENCY_BANDS * 10)

    chunks = 20
    bins = 20
    points_per_bin = self.detection_buffer_size // bins
    spectrogram = np.zeros([chunks, bins])
    print(len(fft), '\n')
    for i in range(chunks):
        data = np.fromstring(self.stream.read(self.detection_buffer_size, exception_on_overflow=False), dtype=np.int16)
        fft = self.fft(data)
        fft = [np.mean(fft[x:(x+1)*points_per_bin]) for x in range(bins)]
        spectrogram[i, :] = fft
    print(spectrogram)

    return np.log(spectrogram)

def spectrogram(wave, to_decibels=True):
    overlap = config.FFT_LENGTH - config.RECORDING_LENGTH // (config.TIMESTEPS + 1)
    config.spectrogram_config['noverlap'] = overlap
    frequencies, times, spectrogram = scipy.signal.spectrogram(
        x=wave, 
        **config.spectrogram_config)

    if to_decibels:
        spectrogram = librosa.power_to_db(spectrogram)
    return spectrogram

def mfcc(wave=None, spectrogram=None):
    mfcc = librosa.feature(y=wave, S=spectrogram, sr=config.SAMPLE_RATE)
    return mfcc

def melspectrogram(wave, normalize=False):
    hop_length = len(wave) // (config.TIMESTEPS + 1)
    # config.melspectrogram['hop_length'] = hop_length
    wave = wave.astype(np.float32)
    mel = librosa.feature.melspectrogram(
        y=wave,
        hop_length=hop_length,
        sr=config.SAMPLE_RATE, 
        n_fft=config.FFT_LENGTH,
        fmin=config.SPECTROGRAM_LOW,
        fmax=config.SPECTROGRAM_HIGH,
        n_mels=config.FREQUENCY_BANDS)

    # mel = np.clip(mel, 10, 255)
    print(mel.max())
    decibels = librosa.power_to_db(mel)
    print(decibels.max())
    decibels = np.clip(decibels, 10, 120) * 2
    # decibels = decibels/120 * decibels.max()
    # if normalize: decibels = scale(decibels)
    # decibels = scale(decibels)
    return decibels
    
def scale(wave):
    """
    Convert wave array to float format in range [0-1]
    """
    min_value = np.min(wave)
    scaled = (wave - min_value) / float((np.max(wave) - min_value))
    print(scaled.max())
    scaled = (scaled * 255).astype(np.int16)
    print(scaled.max())
    return scaled

def fft(wave):
    """
    Returns:

    """
    fft = np.fft.fft(wave)
    frequencies = np.fft.fftfreq(len(fft), 1/float(config.SAMPLE_RATE))
    fft = np.nan_to_num(fft)

    return fft, frequencies

def note(freq):
    """
    Returns musical note corresponding to the frequency
    """
    A4 = 440
    C0 = A4 * math.pow(2, -4.75)
    name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        
    h = round(12 * math.log2(freq / C0))
    octave = h // 12
    n = h % 12
    return name[n] + str(octave)
