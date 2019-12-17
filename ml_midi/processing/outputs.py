import mido
import sys, os, subprocess

def decorator_fn(function_to_wrap, *args, **kwargs):
    """
    Decorator for the input function
    """
    def wrapper(function_to_wrap):
        return None
    return wrapper


class BaseOutput(object):
    """
    Contains base methos for sending outputs
    based on classification outcome
    """
    def __init__(self, fn_to_exec, fn_to_term=None, **kwargs):
        self.exec_fn = fn_to_exec
        self.kwargs = kwargs
        self.name = None
        self.fn_to_term = fn_to_term

    def __repr__(self):
        print('{} output:\n')
        self.print_kwargs()

    def send(self):
        self.exec_fn(**self.kwargs)
        self.terminate()
    
    def terminate(self):
        if self.fn_to_term is not None:
            pass

    def print_kwargs(self):
        Pri
        for k, v in self.kwargs:
            print('{} = {}\n')


class MidiOutput(BaseOutput):
    """
    Send midi messages out
    """
    def __init__(self, b1=0, b2=0, b3=0):
        fn = None
        kwargs = dict()
        MidiOutput.__init__(self, fn, **kwargs)
        self.name = 'Midi'

class ShellOutput(BaseOutput):
    """
    Execute a shell command
    """
    def __init__(self, message=''):
        fn = subprocess.Popen()
        # p = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE)
        kwargs = dict(args=message.split(), stdout=subprocess.PIPE)
        ShellOutput.__init__(self, fn, **kwargs)
        self.name = 'Shell'