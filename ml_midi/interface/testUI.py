from PySide2 import QtCore, QtWidgets, QtGui
import sys, random, os, time
import numpy as np
from ml_midi.interface import ParameterSpinBox, ParameterGroup, MainWidget
# from ml_midi.processing import AudioIO, Dataset, DataSample, Midi
# from ml_midi.learning import RetardedClassifier
# from .dataset import DatasetView
# from .record import RecordView
# from .imagedata import ModelView
import qtmodern.styles
import qtmodern.windows
from ml_midi.config import ConfigManager as config

from ml_midi.interface import ActionComboBox, SettingsAction, MidiAction, PlaySampleAction


class Window(QtWidgets.QMainWindow):
    def __init__(self):

        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName('FFT stuff')
        self.app.setStyle('Fusion')
        self.app.setFont(QtGui.QFont('Courier New', 8))
        self.app.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus, False)
        qtmodern.styles.dark(self.app)
        super(Window, self).__init__()
        self.setGeometry(800, 400, 2000, 300)

        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        help_action = QtWidgets.QAction('Haelp', self)
        help_action.setShortcut('F1')
        help_action.setStatusTip('Help')
        help_action.triggered.connect(self.showdialog)

        self.statusBar()
        sa = SettingsAction(parent=self)
        ma = MidiAction(parent=self)
        self.ps = PlaySampleAction(parent=self)
        
        menu = self.menuBar()
        file = menu.addMenu('&File')
        actions = [ma, sa, self.ps, exit_action]
        file.addActions(actions)
        
        help_menu = menu.addMenu('&Help')
        help_menu.addAction(help_action)

        toolbar = self.addToolBar('Exit')
        toolbar.addActions(actions)

        
        # main = ActionComboBox(parent=self, actions=actions[1:])
        # main = QtInterface(parent=self)
        
        parameters = ['THRESHOLD', 'TIMESTEPS', 'DETECTION_SAMPLE_SIZE',
                      'SPECTROGRAM_LOW', 'SPECTROGRAM_HIGH', 'FREQUENCY_BANDS',
                      'TIMESTEPS', 'FFT_LENGTH']
        main = MainWidget(self)

        self.setCentralWidget(main)

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

    def settings_menu(self):
        print('wow')

    def new_midi(self):
        print('midi')

    def parameter_changed(self):
        attrs = ['THRESHOLD', 'TIMESTEPS', 'DETECTION_SAMPLE_SIZE',
                      'SPECTROGRAM_LOW', 'SPECTROGRAM_HIGH', 'FREQUENCY_BANDS',
                      'TIMESTEPS', 'FFT_LENGTH']
        for attr in attrs:
            print(attr, config.get(attr))

    def play_sample(self):
        print('play')

    def pause(self):
        print('pause')

    def main(self):
        mw = qtmodern.windows.ModernWindow(self)
        mw.show()
        # self.show()
        self.raise_()
        sys.exit(self.app.exec_())



if __name__ == "__main__":

    # interface = QtInterface()
    interface = Window()
    interface.main()
    