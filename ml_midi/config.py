import os, sys

MAIN_DIR = os.path.dirname(os.path.realpath(__file__))
DATA = os.path.join(MAIN_DIR, 'data')

class ParameterContainer(dict):
    # def __init__(self, **kwargs):
    #     super(ParameterContainer,self).__init__()
    def __getattribute__(self, item):
        return self[item]

        
audio_config = dict(
    channels=1,
    chunk_size=128,
    sample_rate=44100,
    device_index=0,
    # detection_threshold=200,
)

net_config = dict(
    filters=[16, 32, 64],
    kernel_size=[3, 3, 3],
    strides=[1, 1, 1],
    fc_layers=[128, 64, 32],
    epochs=10,
)

interface_config = dict(

)

