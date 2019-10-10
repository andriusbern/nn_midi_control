import mido, time
import numpy as np

class Midi(object):
    def __init__(self):
        self.outputs = mido.get_output_names()
        self.port = mido.open_output(self.outputs[0])
        self.mapping = self.load_mapping(None)
        self.channel = 1

    def load_mapping(self, mapping):
        """
        Load a [classifier output<->midi message] hashmap config
        """
        mapping = {
            '0' : self.create_message('note_on', 80, 100),
            '1' : self.create_message('note_on', 20),
            '2' : self.create_message('note_on', 30),
            '3' : self.create_message('note_on', 40),
            '4' : self.create_message('note_on', 50)}
        return mapping

    def send_midi(self, msg_id):
        message = self.mapping[str(msg_id)]
        self.port.send(message)
        if message.type == 'note_on':
            time.sleep(0.001)
            off = mido.Message('note_off', note=message.note)
            self.port.send(off)

    def create_message(self, type, b1, b2=64):

        message = mido.Message(
            type, 
            note=b1,
            velocity=b2)
        
        return message
    