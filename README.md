A smart controller for acoustic instruments that use a microphone or a piezo pickup for amplification. Classify specific taps or gestures to control your digital audio workflow without losing contact with your instrument.

    Given a trigger (e.g. threshold), record a short snippet of a spectrogram of an audiowave (audio signal -> fft -> image)
    Using the interface, repeat step 1 to generate a dataset of different categories of samples that should be classified.
    Train a CNN on the generated data.
    Assign a midi message to each of the labels.

