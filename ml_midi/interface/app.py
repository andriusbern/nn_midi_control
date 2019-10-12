from PyQt5 import QtCore, QtWidgets, QtGui
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


        main = QtInterface()
        self.setCentralWidget(main)

        self.setGeometry(200, 200, 2000, 600)
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
        # msg.buttonClicked.connect(msgbtn)
	
        retval = msg.exec_()

    def main(self):
        mw = qtmodern.windows.ModernWindow(self)
        mw.show()
        self.raise_()
        sys.exit(self.app.exec_())
        
class QtInterface(QtWidgets.QWidget):
    def __init__(self, **kwargs):
        super(QtInterface, self).__init__()
        
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

    def set_data(self, table, parameters, name):
        # parameters = config.mod_config
        table.insertColumn(table.columnCount())
        headers = []
        for n, key in enumerate(parameters.keys()):
            headers.append('{:23}'.format(key))
            val = str(parameters[key])
            item = QtWidgets.QTableWidgetItem(val)
            table.insertRow(table.rowCount())
            table.setRowHeight(n, 10)
            table.setItem(n, 0, item)
            i = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            i.setSliderPosition(20)
            if table == self.parameter_table:
                i.valueChanged.connect(self.par_changed)
            else:
                i.valueChanged.connect(self.spec_changed)
            
            table.setCellWidget(n, 1, i)

        table.setColumnWidth(0, 100)
        table.setColumnWidth(1, 200)
        
        table.setHorizontalHeaderLabels([name])
        table.setVerticalHeaderLabels(headers)

    def par_changed(self, val):
        try:
            rows = sorted(set(index.row() for index in
                        self.parameter_table.selectedIndexes()))[0]
            
            # index = self.parameter_table.selectionModel().selectedRows()[0]
            obj = self.parameter_table.item(rows, 0)
            print(obj)
            obj.setText(str(int(obj.text())+val))
        except:
            pass

    def spec_changed(self, val):
        try:
            rows = sorted(set(index.row() for index in
                        self.spec_table.selectedIndexes()))[0]
            
            # index = self.parameter_table.selectionModel().selectedRows()[0]
            obj = self.spec_table.item(rows, 0)
            print(obj)
            obj.setText(str(int(obj.text())+val))
        except:
            pass

    def table_changed(self, item):
        row = item.row()
        parent = item.tableWidget()
        parameter = parent.verticalHeader().model().headerData(row, QtCore.Qt.Vertical)
        parameter = parameter.strip()
        data_type = type(config.mod_config[parameter])
        data = data_type(item.text())
        base_val = getattr(config, parameter)
        setattr(config, parameter, data)
        print('Changed {}:  {} --> {}'.format(parameter, base_val, data))
        if self.current_sample is not None:
            spec = self.current_sample.create_spectrogram()
            self.record_view.update_spectrogram(spec)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
            try:
                self.env.close()
            except:
                pass

    def setup(self):
        self.layout = QtWidgets.QGridLayout()

        self.parameter_table = QtWidgets.QTableWidget(4, 1)
        self.set_data(self.parameter_table, config.recording_config, 'Recording')
        self.parameter_table.itemChanged.connect(self.table_changed)

        self.spec_table = QtWidgets.QTableWidget(0, 1)
        self.set_data(self.spec_table, config.spec_config, 'Spectrogram')
        self.spec_table.itemChanged.connect(self.table_changed)

        box = QtWidgets.QGroupBox('Parameters')
        temp = QtWidgets.QGridLayout()
        temp.addWidget(self.parameter_table, 1, 2, 1, 1)
        temp.addWidget(self.spec_table, 2, 2, 1, 1)
        temp.addWidget(self.model_view, 3, 2, 1, 1)
        temp.setColumnMinimumWidth(2, 500)
        temp.setRowMinimumHeight(1, 80)
        temp.setRowMinimumHeight(3, 350)
        box.setLayout(temp)

        self.layout.addWidget(self.record_view, 1, 3, 1, 1)
        self.layout.addWidget(self.dataset_view, 1, 1, 1, 1)
        self.layout.addWidget(box, 1, 2, 1, 1)
        # self.layout.addWidget(self.parameter_table, 1, 2, 1, 1)
        # self.layout.addWidget(self.spec_table, 2, 2, 1, 1)
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

    # def main(self):
    #     mw = qtmodern.windows.ModernWindow(self)
    #     mw.show()
    #     # self.show()
    #     self.raise_()
    #     sys.exit(self.app.exec_())