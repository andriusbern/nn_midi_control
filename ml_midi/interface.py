from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg
import sys, random, os
import numpy as np
from audio import pyaudioWrapper
from data_handler import DataHandler
import config

class Interface(QtWidgets.QWidget):
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName('FFT stuff')
        super(Interface, self).__init__()
        self.audio = pyaudioWrapper(**config.audio_config) 
        self.timer = QtCore.QTimer()
        self.trigger_timer = QtCore.QTimer()

        self.threshold = 30000
        self.bins = 20
        self.recording = False
        self.recording_frame = 0
        self.detection_buffer = 1024
        self.recording_buffer = 64
        self.recording_length = 20
        self.fft_cutoff = 0.4
        self.current_chunk = self.detection_buffer
        self.spectrogram = np.zeros([self.recording_length, self.bins])
        self.label = '0'
        self.dataset = 'default'

        self.data_handler = DataHandler()
        self.setup()

    def setup(self):
        self.layout = QtWidgets.QGridLayout()

        self.record_button = QtWidgets.QPushButton('Record')
        self.record_button.setText('Record')
        self.record_button.clicked.connect(self.record)

        self.loop_button = QtWidgets.QPushButton('Loop')
        self.loop_button.setText('Loop')
        self.loop_button.clicked.connect(self.loop)

        self.record_sample_button = QtWidgets.QPushButton('Loop')
        self.record_sample_button.setText('Record s')
        self.record_sample_button.clicked.connect(self.wait_for_threshold)

        self.sample_display = pg.PlotWidget()
        self.sample_display.getPlotItem().setTitle('Sample')
        self.sample_display.setYRange(-20000, 20000)

        self.fft_display = pg.PlotWidget()
        self.fft_display.getPlotItem().setTitle('FFT')
        self.fft_display.plotItem.setLogMode(True, False)
        self.fft_display.setYRange(0, 1000000)

        self.spec = pg.PlotItem()
        self.spectrogram_display = pg.ImageView(view=self.spec)
        self.spectrogram_display.getView().invertY(False)

        self.status_box = QtWidgets.QLineEdit()
        self.status_box.setText('Values.')

        self.label_category = QtWidgets.QLabel()
        self.label_category.setText('Sample category')
        self.label_box = QtWidgets.QLineEdit()
        self.label_box.setText(self.label)
        self.label_box.textChanged.connect(self.update_label)

        self.dataset_label = QtWidgets.QLabel()
        self.dataset_label.setText('Dataset name')
        self.dataset_name_box = QtWidgets.QLineEdit()
        self.dataset_name_box.setText(self.dataset)
        self.dataset_name_box.textChanged.connect(self.change_dataset)

        # self.parameter_table = QtWidgets.QTableWidget(0, 1)
        # self.set_data()
        # self.parameter_table.itemChanged.connect(self.table_changed)

        self.layout.addWidget(self.record_button, 1, 1, 1, 1)
        self.layout.addWidget(self.loop_button, 1, 2, 1, 1)
        self.layout.addWidget(self.dataset_label, 2, 1, 1, 1)
        self.layout.addWidget(self.dataset_name_box, 2, 2, 1, 1)
        self.layout.addWidget(self.label_category, 3, 1, 1, 1)
        self.layout.addWidget(self.label_box, 3, 2, 1, 1)
        self.layout.addWidget(self.sample_display, 4, 1, 1, 2)
        self.layout.addWidget(self.fft_display, 5, 1, 1, 2)
        self.layout.addWidget(self.status_box, 6, 1, 1, 1)
        self.layout.addWidget(self.spectrogram_display, 1, 3, 5, 1)
        self.layout.setColumnMinimumWidth(3, 400)
        # self.layout.addWidget(self.parameter_table, 1, 3, 6, 1)

        self.setLayout(self.layout)

    def record(self):
        data = self.audio.get_chunk(self.current_chunk)
        fft = self.audio.fft(data)
        binned = self.audio.fft(data, bins=self.bins)
        self.update_fft(fft)
        self.update_sample(data)
        if max(data) > self.threshold and not self.recording:
            self.recording = True
            self.current_chunk = self.recording_buffer
        if self.recording:
            self.spectrogram[self.recording_frame, :] = binned
            self.recording_frame += 1
            print('Recording... {}/{}'.format(self.recording_frame, self.recording_length), end='\r')
        if self.recording_frame >= self.recording_length:
            self.recording = False
            self.recording_frame, self.current_chunk = 0, self.detection_buffer
            self.data_handler.write_image(self.spectrogram, self.dataset, self.label)
        self.update_spectrogram()

    def loop(self):
        self.timer.timeout.connect(self.record)
        self.timer.start(0.1)
        self.status_box.setText('Looping')

    def record_sample(self):
        # print(' ')
        if self.audio.triggered(10000):
            print('Recording')
            data = self.audio.get_chunk()
            fft = self.audio.fft(data)

    def wait_for_threshold(self):
        self.trigger_timer.timeout.connect(self.record_sample)
        self.trigger_timer.start(0.1)
        self.status_box.setText('Waiting for thresh')

    def set_data(self):
        parameters = config.audio_config
        headers = []
        for n, key in enumerate(parameters.keys()):
            headers.append(key)
            val = str(parameters[key])
            item = QtWidgets.QTableWidgetItem(val)
            self.parameter_table.insertRow(self.parameter_table.rowCount())
            self.parameter_table.setRowHeight(n, 10)
            self.parameter_table.setItem(n, 0, item)
        self.parameter_table.setHorizontalHeaderLabels('Parameters')
        self.parameter_table.setColumnWidth(0, 350)
        self.setVerticalHeaderLabels(headers)

    def table_changed(self, item):
        row = item.row()
        parent = item.tableWidget()
        parameter = parent.verticalHeader().model().headerData(row, QtCore.Qt.Vertical)
        data_type = type(config.audio_config[parameter])
        config.audio_config[parameter] = data_type(item.text())
    
    def stop(self):
        self.trigger_timer.stop()
        self.timer.stop()

    def update_fft(self, data):
        data = [abs(x) for x in data]
        
        self.fft_display.getPlotItem().plot(clear=True).setData(data)

    def update_spectrogram(self):
        self.spectrogram_display.setImage(self.spectrogram)

    def update_sample(self, data):
        self.sample_display.getPlotItem().plot(clear=True).setData(data)

    def update_label(self):
        self.label = str(self.label_box.text())

    def change_dataset(self):
        self.dataset = str(self.dataset_name_box.text())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
            try:
                self.env.close()
            except:
                pass

    def main(self):
        self.show()
        self.raise_()
        sys.exit(self.app.exec_())


if __name__ == "__main__":

    interface = Interface()
    interface.main()