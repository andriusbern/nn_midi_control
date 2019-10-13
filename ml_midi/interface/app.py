from PySide2 import QtCore, QtWidgets, QtGui
import sys, random, os, time
import numpy as np
from ml_midi.processing import AudioIO, Dataset, DataSample, Midi
from ml_midi.learning import RetardedClassifier
from .dataset import DatasetView
from .record import RecordView
from .imagedata import ModelView
import qtmodern.styles
import qtmodern.windows


import ml_midi.config as config

class Window(QtWidgets.QMainWindow):
    def __init__(self):

        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName('FFT stuff')
        self.app.setStyle('Fusion')
        self.app.setFont(QtGui.QFont('Cursive', 8))
        qtmodern.styles.dark(self.app)
        super(Window, self).__init__()

        exit_action = QtGui.QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        help_action = QtGui.QAction('Haelp', self)
        help_action.setShortcut('F1')
        help_action.setStatusTip('Help')
        help_action.triggered.connect(self.showdialog)

        self.statusBar()

        menu = self.menuBar()
        file = menu.addMenu('&File')
        file.addAction(exit_action)

        help_menu = menu.addMenu('&Help')
        help_menu.addAction(help_action)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit_action)

        main = QtInterface(parent=self)
        self.setCentralWidget(main)

        self.setGeometry(200, 200, 1400, 600)
        self.show()

    def display_help(self):
        msg = QtWidgets.QMessageBox()
        msg.setText('Nice.')

    def showdialog(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)

        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        retval = msg.exec_()

    def main(self):
        mw = qtmodern.windows.ModernWindow(self)
        mw.show()
        self.raise_()
        sys.exit(self.app.exec_())
        
class QtInterface(QtWidgets.QWidget):
    def __init__(self, parent, **kwargs):
        super(QtInterface, self).__init__(parent=parent)
        
        self.audio = AudioIO(**config.audio_config) 
        self.midi = Midi()
        self.classifier = RetardedClassifier()
        
        self.record_view = RecordView(self)
        self.current_sample = None
        self.dataset_view = DatasetView(self)
        self.model_view = ModelView(self)

        self.setup()
        self.dataset = None

    def new_recording_made(self):
        self.dataset_view.update_summary()

    def setup(self):
        self.layout = QtWidgets.QGridLayout()

        box = QtWidgets.QGroupBox('Parameters')
        temp = QtWidgets.QGridLayout()
        temp.addWidget(self.model_view, 1, 1, 1, 1)
        box.setLayout(temp)

        self.layout.addWidget(self.record_view, 1, 3, 1, 1)
        self.layout.addWidget(self.dataset_view, 1, 1, 1, 1)
        self.layout.addWidget(box, 1, 2, 1, 1)
        self.layout.setColumnMinimumWidth(2, 300)

        self.setLayout(self.layout)

    def sample_selected(self, sample_no):
        self.record_view.stop()
        sample = self.current_sample = self.dataset.get_sample(sample_no)
        print(sample, sample.id)
        self.audio.playback(sample.wave)
        self.record_view.update_spectrogram(sample.create_spectrogram())
        self.record_view.update_sample(sample.wave)
        self.record_view.console.setPlainText('Playing sample {}'.format(sample_no))

    def dataset_selected(self):
        self.dataset = self.dataset_view.dataset
        self.record_view.loop_button.setEnabled(True)
