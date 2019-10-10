from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg
import sys, random, os, time
import numpy as np
from ml_midi.processing import AudioIO, Dataset, DataSample, Midi
from ml_midi.learning import RetardedClassifier
import ml_midi.config as config
from QLed import QLed

# class Application(QtWidgets.QMainWindow):
"""
# TODO:
    - Tabs:
        - https://pythonspot.com/pyqt5-tabs/
        - Recording
            1. Same as the QtInterface class
            2. Model selection, config loading

        - Datasets, training
            1. Directory browsing
            2. Model config
            3. Training 
"""
class QtInterface(QtWidgets.QWidget):
    def __init__(self, **kwargs):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName('FFT stuff')
        self.app.setStyle('Breeze')
        
        super(QtInterface, self).__init__()
        self.setGeometry(1000, 600, 600, 400)
        self.audio = AudioIO(**config.audio_config) 
        self.midi = Midi()
        self.classifier = RetardedClassifier()
        self.timer = QtCore.QTimer()

        self.running = False
        self.recording = False
        self.current_max = 0
        self.spectrogram = np.ones([config.FREQUENCY_BANDS, config.TIMESTEPS])
        self.label = '0'
        self.dataset_name = 'new'
        self.dataset = Dataset(self.dataset_name)

        self.setup()
        self.update_console()

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
            data, _ = self.audio.record(config.DETECTION_SAMPLE_SIZE)
            self.update_sample(data)
            self.current_max = max(data)
            if self.current_max > config.THRESHOLD:
                self.record_led.value, self.recording = True, True

    def record_sample(self):
        t0 = time.time()
        data, raw = self.audio.record(config.RECORDING_LENGTH)

        sample = self.dataset.new_sample(
            wave=data, 
            bytestring=raw, 
            label=self.label,
            save=True)

        self.spectrogram = np.flip(sample.spectrogram.T)[::-1]
        self.audio.playback(data)

        self.update_spectrogram()
        y = self.classifier.classify(self.spectrogram)
        self.midi.send_midi(msg_id=y)
        self.time_taken = time.time() - t0
        self.update_console(y=y)
        # print(y, time.time() - t0)

    def update_console(self, y=None):
        sep = '=' * 20
        if self.running:
            status = 'Waiting for threshold...'
        if self.recording:
            status = 'Recording...'
        else:
            status = 'Stopped.'
        message = sep + '\nStatus: {}\n'.format(status)
        message += '    Signal max: {:4}\n'.format(self.current_max)
        if y is not None:
            message += sep + '\nClassification\n'
            message += '    Class: {}\n'.format(y)
            message += '    Time taken: {:.2f}\n'.format(self.time_taken)
        self.console.setPlainText(message)

    def set_data(self):
        parameters = config.mod_config
        headers = []
        for n, key in enumerate(parameters.keys()):
            headers.append(key)
            val = str(parameters[key])
            item = QtWidgets.QTableWidgetItem(val)
            self.parameter_table.insertRow(self.parameter_table.rowCount())
            self.parameter_table.setRowHeight(n, 10)
            self.parameter_table.setItem(n, 0, item)
        self.parameter_table.setColumnWidth(0, 350)
        self.parameter_table.setVerticalHeaderLabels(headers)

    def table_changed(self, item):
        row = item.row()
        parent = item.tableWidget()
        parameter = parent.verticalHeader().model().headerData(row, QtCore.Qt.Vertical)
        data_type = type(config.mod_config[parameter])
        data = data_type(item.text())
        base_val = getattr(config, parameter)
        setattr(config, parameter, data)
        print('Changed {}:  {} --> {}'.format(parameter, base_val, data))
    
    def update_spectrogram(self):
        self.spectrogram_display.setImage(self.spectrogram)

    def update_sample(self, data):
        self.sample_display.getPlotItem().plot(clear=True).setData(data)

    def update_label(self):
        self.label = str(self.label_box.text())

    def change_dataset(self):
        self.dataset_name = str(self.dataset_name_box.text())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
            try:
                self.env.close()
            except:
                pass

    def setup(self):
        self.layout = QtWidgets.QGridLayout()

        self.record_led = QLed(self, onColour=QLed.Red, shape=QLed.Circle)
        self.record_led.value = False

        self.loop_button = QtWidgets.QPushButton('Loop')
        self.loop_button.setText('Loop')
        self.loop_button.clicked.connect(self.loop)

        self.sample_display = pg.PlotWidget()
        self.sample_display.getPlotItem().setTitle('Sample')
        self.sample_display.setYRange(-1000, 1000)

        self.fft_display = pg.PlotWidget()
        self.fft_display.getPlotItem().setTitle('FFT')
        self.fft_display.plotItem.setLogMode(True, False)
        self.fft_display.setYRange(-10000, 10000)

        self.spectrogram_display = pg.ImageView()

        self.console = QtWidgets.QPlainTextEdit()
        self.console.setFixedSize(250, 200)
        # self.console.setText('Values.')

        self.label_category = QtWidgets.QLabel()
        self.label_category.setText('Sample category:')
        self.label_box = QtWidgets.QLineEdit()
        self.label_box.setText(self.label)
        self.label_box.textChanged.connect(self.update_label)

        self.dataset_label = QtWidgets.QLabel()
        self.dataset_label.setText('Dataset name:')
        self.dataset_name_box = QtWidgets.QLineEdit()
        self.dataset_name_box.setText(self.dataset_name)
        self.dataset_name_box.textChanged.connect(self.change_dataset)

        self.parameter_table = QtWidgets.QTableWidget(0, 1)
        self.set_data()
        self.parameter_table.itemChanged.connect(self.table_changed)

        self.layout.addWidget(self.record_led, 1, 1, 1, 2)
        self.layout.addWidget(self.loop_button, 2, 1, 1, 2)
        self.layout.setRowMinimumHeight(1, 50)
        self.layout.setRowMinimumHeight(2, 100)

        self.layout.addWidget(self.dataset_label, 3, 1, 1, 1)
        self.layout.addWidget(self.dataset_name_box, 3, 2, 1, 1)
        self.layout.addWidget(self.label_category, 4, 1, 1, 1)
        self.layout.addWidget(self.label_box, 4, 2, 1, 1)
        self.layout.setColumnMinimumWidth(2, 50)

        self.layout.addWidget(self.spectrogram_display, 6, 1, 1, 3)
        self.layout.addWidget(self.console, 6, 4, 1, 1)
        self.layout.addWidget(self.sample_display, 1, 3, 5, 1)
        self.layout.addWidget(self.parameter_table, 1, 4, 5, 1)
        self.layout.setColumnMinimumWidth(3, 200)
        self.layout.setColumnMinimumWidth(4, 250)
        # self.layout.setColumnMinimumWidth(5, 200)

        self.setLayout(self.layout)

    def main(self):
        self.show()
        self.raise_()
        sys.exit(self.app.exec_())

if __name__ == "__main__":

    interface = QtInterface()
    interface.main()