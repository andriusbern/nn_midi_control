import mido

class MidiController(object):
    def __init__(self):
        pass

class NNMidiController(MidiController):
    def __init__(self, net):
        self.net = None

    def load_model(self, name):
        pass

    def read_input(self, input):
        output = 0
        return output