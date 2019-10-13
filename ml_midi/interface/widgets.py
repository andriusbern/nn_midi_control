from PySide2 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
from ml_midi.config import ConfigManager as config
from .actions import MidiAction, PlaySampleAction
import os
import numpy as np

def get_icon(name):
    icon_path = os.path.join(config.ICONS, name+'.svg')
    return icon_path


class ActionComboBox(QtWidgets.QComboBox):

    def __init__(self, parent, actions):
        super(ActionComboBox, self).__init__(parent=parent)

        self.par = parent
        self.action_list = actions

        icon = QtGui.QIcon(QtGui.QPixmap(get_icon('Default')))
        self.insertItem(0, icon, 'New output')
        self.model().item(0).setEnabled(False)
        self.setup(actions)

        self.activated.connect(self.selection)

    def setup(self, actions):
        for i, action in enumerate(actions):
            self.addItem(action.icon(), action.name)

    def selection(self):
        """
        Trigger an action based on selection
        """
        self.currentIndex()
        self.action_list[self.currentIndex()-1].trigger()
        self.setCurrentIndex(0)

class ActionButton(QtWidgets.QPushButton):
    def __init__(self, parent, action):
        super(ActionButton, self).__init__(parent=parent)

        self.action = action
        self.name = action.name
        # self.addAction(action)
        self.setCheckable = True
        # self.setIcon(action.icon())
        self.setText('')
        self.setChecked(True)
        self.toggle()
        self.toggled.connect(action.toggle())
        names = ['Play', 'Pause']

   
        if names is None:
            names = [self.name]
        # fns = [QtGui.QIcon, QtGui.QIcon.Mode.Active]
        for i,name in enumerate(names):
            path = os.path.join(config.ICONS, self.name+'.svg')
            icon = QtGui.QIcon(parent=self)
            icon.addPixmap(QtGui.QPixmap(path)) #, fns[i]
        self.setIcon(icon)
    

class ParameterSpinBox(QtWidgets.QWidget):
    def __init__(self, parent, parameter):
        super(ParameterSpinBox, self).__init__(parent=parent)

        self.par = parent
        self.parameter = parameter
        self.translated = config.translate(parameter)
        self.scale = config.ranges[parameter]
        val = config.get(parameter)
        
        self.spin_box = QtWidgets.QSpinBox()
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.set_ranges()
        self.spin_box.setValue(val)
        self.spin_box.setMinimumWidth(70)
        self.slider.setValue(self.find_nearest(val))
        self.slider.valueChanged[int].connect(self.value_changed)
        self.spin_box.valueChanged[int].connect(self.update_slider)
        
        name = ' ' * (23 - len(self.translated)) + self.translated + ':'
        self.label = QtWidgets.QLabel(name)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.spin_box)
        layout.addWidget(self.slider)
        # layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def set_ranges(self):
        self.spin_box.setRange(self.scale[0], self.scale[-1])
        self.slider.setRange(0, len(self.scale)-1)
    
    def update_slider(self):
        value = self.find_nearest(self.spin_box.value())
        self.slider.setValue(value)

    def value_changed(self, value):
        value = self.scale[self.slider.value()]
        self.spin_box.setValue(value)
        self.par.parameter_changed()
        setattr(config, self.parameter, value)

    def find_nearest(self, value):
        array = np.asarray(self.scale)
        idx = (np.abs(array - value)).argmin()
        return idx
    
class ParameterGroup(QtWidgets.QGroupBox):
    def __init__(self, name, parent, parameters):
        super(ParameterGroup, self).__init__(name, parent=parent)
        self.parameter_dials = []
        self.par = parent

        layout = QtWidgets.QVBoxLayout()
        for parameter in parameters:
            widget = ParameterSpinBox(parent, parameter)
            self.parameter_dials.append(widget)
            layout.addWidget(widget)
            layout.addSpacing(-25)
        layout.addSpacing(25)
        self.setLayout(layout)

class ParameterContainer(QtWidgets.QGroupBox):
    def __init__(self, name, parent):
        super(ParameterContainer, self).__init__(name, parent=parent)

        self.par = parent

        audio = ['THRESHOLD', 'TIMESTEPS', 'DETECTION_SAMPLE_SIZE']
        self.audio_parameters = ParameterGroup('Audio Parameters', self.par, audio)

        image = ['SPECTROGRAM_LOW', 'SPECTROGRAM_HIGH', 'FREQUENCY_BANDS',
                'TIMESTEPS', 'FFT_LENGTH']
        self.image_parameters = ParameterGroup('Spectrogram Parameters', self.par, image)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.audio_parameters)
        layout.addWidget(self.image_parameters)
        self.setLayout(layout)

            
class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MainWidget, self).__init__(parent=parent)
        self.par = parent
        self.create_layout()

    def create_layout(self):
        
        # Parameters
        
        self.parameter_widget = ParameterContainer('Parameters', self.par)
        self.sample_widget = SampleWidget('Sample Display', self.par)
        self.dataset_view = DatasetWidget(self.par)
        
        # Layout
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.parameter_widget, 1, 2, 1, 1)
        layout.addWidget(self.sample_widget, 1, 3, 1, 1)
        layout.addWidget(self.dataset_view, 1, 4, 1, 1)
        self.setLayout(layout)

class SampleWidget(QtWidgets.QGroupBox):
    def __init__(self, name, parent):
        super(SampleWidget, self).__init__(name, parent=parent)
        self.par = parent

        self.current_sample = None

        self.tracker = QtWidgets.QSlider(QtGui.Qt.Horizontal)
        self.tracker.setValue(5)
        self.tracker.setRange(0,100)

        self.sample_display = pg.PlotWidget()
        self.sample_display.setYRange(-20000, 20000)
        self.sample_display.setXRange(0, 10000)
        self.sample_display.getPlotItem().setFixedHeight(100)
        
        self.line = pg.InfiniteLine()
        self.sample_display.addItem(self.line)
        self.seek(5)

        self.tracker.valueChanged[int].connect(self.seek)
        self.image_view = pg.ImageView()
        self.image_view.ui.histogram.close()
        self.image_view.ui.menuBtn.close()
        self.image_view.ui.roiBtn.close()
        self.image_view.getImageItem().setBorder(200)
        print(self.image_view.getImageItem().height())

        self.set_layout()


    def set_layout(self):

        self.sample_display.setBackground(None)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.image_view, 1, 1, 1, 1)
        layout.addWidget(self.sample_display, 2, 1, 1, 1)
        layout.addWidget(self.tracker, 3, 1, 1, 1)

        layout.setRowMinimumHeight(1, 200)
        layout.setRowMinimumHeight(2, 120)
        layout.setRowStretch(3, 0)

        self.setLayout(layout)

    def set_sample(self, sample):
        self.current_sample = sample

    def set_image(self, sample):
        pass

    def seek(self, value):
        self.line.setValue(value*100)


    

class AudioWidget(QtWidgets.QWidget):
    pass

class DatasetWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(DatasetWidget, self).__init__(parent=parent)
        self.par = parent

        self.dataset = None

        self.new_label_box = ActionComboBox(self.par, [MidiAction(parent=self.par)])
        self.file_browser = FileBrowser(self.par, self)
        
        self.play_button = ActionButton(self.par, self.par.ps)
        
        
        self.dataset_selection = DirectoryComboBox(self.par, config.AUDIO)
        self.dataset_selection.activated[str].connect(self.change_dataset)

        self.set_layout()

    def set_layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.new_label_box)
        layout.addWidget(self.file_browser)
        layout.addWidget(self.dataset_selection)
        layout.addWidget(self.play_button)
        self.setLayout(layout)

    def change_dataset(self, path):
        path = os.path.join(config.AUDIO, path)
        self.file_browser.update_path(path)

class FileBrowser(QtWidgets.QTreeView):
    def __init__(self, parent, datawidget):
        super(FileBrowser, self).__init__(parent=parent)
        self.par = parent
        self.data_widget = datawidget

        self.model = QtGui.QFileSystemModel()
        self.setModel(self.model)
        self.setAnimated(False)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.update_path(config.MAIN_DIR)

    def update_path(self, directory):
        self.setRootIndex(self.model.index(directory))
        self.doubleClicked.connect(self.play_sample)
        self.model.setRootPath(directory)

    def play_sample(self):
        pass

        # self.label_selection.clear()
        # self.label_selection.addItems(self.dataset.hashmap.keys())
        # self.label_selection.setEnabled(True)
        # self.create_label_button.setEnabled(True)

    
# class 

class DirectoryComboBox(QtWidgets.QComboBox):
    def __init__(self, parent, directory):
        super(DirectoryComboBox, self).__init__(parent=parent)
        self.fsm  = QtGui.QFileSystemModel()
        self.update_path(directory)
    
    def update_path(self, directory):
        index = self.fsm.setRootPath(directory)
        self.setModel(self.fsm)
        self.setRootModelIndex(index)

    def check_existing(self, value):
        return True if self.dataset_selection.findData(value) >= 0 else False

