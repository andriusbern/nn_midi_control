from PySide2 import QtCore, QtWidgets, QtGui
import sys, random, os, time
import numpy as np
from ml_midi.interface import ParameterSpinBox, ParameterGroup, MainWidget
from ml_midi.processing import AudioIO, Dataset, DataSample, Midi
# from ml_midi.learning import RetardedClassifier
# from .dataset import DatasetView
# from .record import RecordView
# from .imagedata import ModelView

import qtmodern.styles
import qtmodern.windows

from ml_midi.interface import *
from ml_midi.config import ConfigManager as config


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle('Neural Midi Control')
        self.dimensions = [800, 400, 1500, 900]
        self.setGeometry(*self.dimensions)
        # qtmodern.styles.dark(self)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(config.ICONS, 'App.svg')))
        self.setWindowIconText('NMC')
        self.settings = None
        
        self.midi = Midi()

        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.setIcon(QIcon(QPixmap(os.path.join(config.ICONS, 'Exit'))))
        exit_action.triggered.connect(self.close)

        help_action = QtWidgets.QAction('Haelp', self)
        help_action.setShortcut('F1')
        help_action.setStatusTip('Help')
        help_action.triggered.connect(self.showdialog)

        self.status_bar = self.statusBar()
        sa = SettingsAction(parent=self)
        # ma = MidiAction(parent=self)
        # self.ps = PlaySampleAction(parent=self)
        # self.nl = NewLabelAction(parent=self)
        
        menu = self.menuBar()
        file = menu.addMenu('&File')
        # actions = [ma, sa, self.ps, self.nl, exit_action]
        actions = [sa, exit_action]
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
        self.main_widget = MainWidget(self)

        self.setCentralWidget(self.main_widget)

        self.show()

    def display_help(self):
        msg = QtWidgets.QMessageBox()
        msg.setText('Nice.')

    def showdialog(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)

        msg.setText("SEND HELP")
        msg.setWindowTitle("HELP ME")
        msg.setDetailedText("Du gaideliai ultravioletinius zirnius kule.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        retval = msg.exec_()

    def settings_menu(self):
        self.settings = SettingsMenu(self.main_widget.sample_widget)
        self.settings.setGeometry(QtCore.QRect(1500, 600, 600, 400))
        self.settings.show()
        self.settings.raise_()

    def new_midi(self):
        print('midi')


    # def play_sample(self, status):
    #     if status:
    #         print('play')
    #         sample = self.main_widget.sample_widget.current_sample
    #         print(sample.wave)
    #         # self.audio.playback(sample.wave)

    #     else:
    #         print('pause')

    def new_label(self):
        print('lab')


class App(QtWidgets.QApplication):
    def __init__(self, *args):
        QtWidgets.QApplication.__init__(self, *args)
        qtmodern.styles.dark(self)
        # self.setFont(QFont('', 8))
        self.window = Window()
        # self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
        self.window.show()

    def closeEvent( self ):
        self.exit(0)
    
    def main(self, args):
        # mw = qtmodern.windows.ModernWindow(self.window)
        # mw.show()
        self.window.show()
        self.window.raise_()
        sys.exit(self.exec_())
    


if __name__ == "__main__":

    # interface = QtInterface()
    interface = App()
    interface.main(sys.argv)
    