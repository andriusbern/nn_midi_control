from PyQt5 import QtCore, QtWidgets, QtGui
from QLed import QLed
import pyqtgraph as pg
import sys, random, os, time
import numpy as np
from ml_midi.processing import AudioIO
import ml_midi.config as config

class RecordView(QtWidgets.QWidget):
    def __init__(self, parent):
        super(RecordView, self).__init__(parent=parent)
        self.parent = parent
        self.timer = QtCore.QTimer()
        self.running = False
        self.recording = False
        self.current_max = 0
        self.setup()
    
    def loop(self):
        self.running = True
        self.loop_button.setText('Stop')
        self.loop_button.clicked.connect(self.stop)
        self.timer.timeout.connect(self.detect)
        self.timer.start(0.001)
        self.update_console()

    def stop(self):
        self.timer.stop()
        self.timer = QtCore.QTimer()
        self.running = False
        self.loop_button.clicked.connect(self.loop)
        self.update_console()
    
    def detect(self):
        if self.recording:
            self.record_sample()
            self.record_led.value, self.recording = False, False
        else:
            data, _ = self.parent.audio.record(config.DETECTION_SAMPLE_SIZE)
            self.update_sample(data)
            self.current_max = max(data)
            if self.current_max > config.THRESHOLD:
                self.record_led.value, self.recording = True, True
            self.update_console()
        
    def record_sample(self):
        t0 = time.time()
        data, raw = self.parent.audio.record(config.RECORDING_LENGTH)

        sample = self.parent.dataset.new_sample(
            wave=data, 
            bytestring=raw, 
            save=True)

        self.update_spectrogram(sample.create_spectrogram())

        y = 0
        self.time_taken = time.time() - t0
        self.update_console(y=y)
        self.parent.new_recording_made()

    def update_console(self, y=None):
        if self.running:
            status = 'Waiting for threshold...'
        if self.recording:
            status = 'Recording...'
        else:
            status = 'Stopped.'
        message = 'Status: {}\n'.format(status)
        message += '    Signal max: {:4}\n'.format(self.current_max)
        if y is not None:
            message += '\nClassification\n'
            message += '    Class: {}\n'.format(y)
            message += '    Time taken: {:.2f}\n'.format(self.time_taken)
        self.console.setPlainText(message)
    
    def update_spectrogram(self, image):
        image = np.flip(image.T)[::-1]
        self.spectrogram_display.setImage(image)

    def update_sample(self, data):
        data = np.abs(data)
        self.sample_display.getPlotItem().plot(clear=True).setData(data)
    
    def setup(self):
        self.layout = QtWidgets.QGridLayout()

        group = QtWidgets.QGroupBox('Recording')
        
        layout = QtWidgets.QGridLayout()
        group.setLayout(layout)
        self.layout.addWidget(group)

        self.record_led = QLed(self, onColour=QLed.Red, shape=QLed.Circle)
        self.record_led.value = False

        self.loop_button = QtWidgets.QPushButton('Loop')
        self.loop_button.setText('Loop')
        self.loop_button.clicked.connect(self.loop)
        self.loop_button.setEnabled(False)

        self.device_info = QtWidgets.QPushButton('Devices')
        self.device_info.setText('Devices')
        self.device_info.clicked.connect(self.devices)

        self.sample_display = pg.PlotWidget()
        self.sample_display.getPlotItem().setTitle('Sample')
        self.sample_display.setYRange(-20000, 20000)

        self.spectrogram_display = pg.ImageView()
        # self.spectrogram_display.

        self.console = QtWidgets.QPlainTextEdit()
        # self.console.setFixedSize(250, 200)

        layout.addWidget(self.record_led, 1, 1, 1, 2)
        layout.addWidget(self.loop_button, 2, 1, 1, 2)
        layout.addWidget(self.device_info, 3, 1, 1, 2)
        layout.setRowMinimumHeight(1, 50)
        layout.setRowMinimumHeight(2, 100)
        layout.addWidget(self.spectrogram_display, 6, 1, 1, 4)
        layout.setRowMinimumHeight(6, 300)
        layout.setColumnMinimumWidth(3, 600)
        layout.addWidget(self.console, 7, 1, 1, 4)
        layout.addWidget(self.sample_display, 1, 3, 5, 2)
        layout.setColumnMinimumWidth(3, 200)

        self.setLayout(self.layout)

    def devices(self):
        t = self.parent.audio.get_device_info()
        self.console.setPlainText(t)