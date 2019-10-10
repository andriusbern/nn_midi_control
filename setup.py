from setuptools import setup
import time, os

packages = [
    'PyQt5', 
    'pyqtgraph', 
    'pyaudio',
    'python-rtmidi',
    'mido',
    'scipy', 
    'Pillow', 
    'opencv-python', 
    'librosa', 
    'tensorflow']

setup(
    name='ml_midi',
    description='Audio classification and midi control using machine learning.',
    long_description='',
    version='0.2',
    packages=['ml_midi'],
    scripts=[],
    author='Andrius Bernatavicius',
    author_email='andrius.bernatavicius@gmail.com',
    url='none',
    download_url='none',
    install_requires=packages
)

print ("Installation complete.\n")