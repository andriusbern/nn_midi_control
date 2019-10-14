from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import pyqtgraph as pg
from .actions import *
from ml_midi.processing import Dataset, DataSample, AudioIO
import os, time
import numpy as np
from ml_midi.config import ConfigManager as config

def get_icon(name):
    icon_path = os.path.join(config.ICONS, name+'.svg')
    return icon_path

class ToolBar(QToolBar):
    def __init__(self, parent, actions):
        super(ActionComboBox, self).__init__(parent=parent)
        self.addActions(actions)

class ActionComboBox(QComboBox):
    def __init__(self, parent, actions):
        super(ActionComboBox, self).__init__(parent=parent)

        self.par = parent
        self.action_list = actions

        icon = QIcon(QPixmap(get_icon('Default')))
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

class ActionButton(QToolButton):
    def __init__(self, parent, action, name):
        super(ActionButton, self).__init__(parent=parent)

        self.action = action
        self.name = action.name
        self.setText(self.name)
        self.setIcon(action.icon())
        self.setCheckable(True)
        self.toggled.connect(print('nono'))
        
        self.setToolTip(name)

class ToggleButton(QPushButton):
    def __init__(self, parent, names, trigger, status=None):
        super(ToggleButton, self).__init__(parent=parent)
        self.par = parent
        self.setCheckable(True)
        self.names = names
        self.status = status
        self.status_change(False)
        self.clicked[bool].connect(getattr(self.par, trigger))
        self.clicked[bool].connect(self.status_change)

        modes = [QIcon.Mode.Normal, QIcon.Mode.Normal, QIcon.Mode.Disabled]
        fns = [QIcon.State.Off, QIcon.State.On, QIcon.State.Off]
        icon = QIcon(parent=self)
        for i,name in enumerate(self.names):
            path = os.path.join(config.ICONS, name+'.svg')
            print(path)
            icon.addPixmap(QPixmap(path), modes[i], fns[i]) #, fns[i]
        self.setIcon(icon)

    def status_change(self, toggled):
        tip = self.status[1] if toggled else self.status[0]
        self.setStatusTip(tip)
        # self.par.statusBar().showMessage(tip)

    def stop(self):
        self.setChecked(False)

class ClickButton(QPushButton):
    def __init__(self, parent, name, triggers, status=None):
        super(ClickButton, self).__init__(parent=parent)
        self.par = parent
        self.name = name
        self.setStatusTip(status)

        for trigger in triggers:
            self.clicked.connect(trigger)

        icon = QIcon(parent=self)
        path = os.path.join(config.ICONS, name+'.svg')
        print(path)
        icon.addPixmap(QPixmap(path)) #, fns[i]
        self.setIcon(icon)

class ParameterSpinBox(QWidget):
    def __init__(self, parent, parameter):
        super(ParameterSpinBox, self).__init__(parent=parent)

        self.par = parent
        self.parameter = parameter
        self.translated = config.translate(parameter)
        self.scale = config.ranges[parameter]
        val = config.get(parameter)
        
        self.spin_box = QSpinBox()
        self.spin_box.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.slider = QSlider(Qt.Horizontal)
        self.set_ranges()
        self.spin_box.setValue(val)
        self.spin_box.setMinimumWidth(80)
        self.slider.setValue(self.find_nearest(val))
        self.slider.valueChanged[int].connect(self.value_changed)
        self.spin_box.valueChanged[int].connect(self.update_slider)
        
        name = ' ' * (21 - len(self.translated)) + self.translated + ':'
        self.label = QLabel(name)
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.spin_box)
        layout.addWidget(self.slider)
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
        self.par.parameter_changed(self.parameter)
        setattr(config, self.parameter, value)

    def find_nearest(self, value):
        array = np.asarray(self.scale)
        idx = (np.abs(array - value)).argmin()
        return idx
    
class ParameterGroup(QGroupBox):
    def __init__(self, name, parent, parameters):
        super(ParameterGroup, self).__init__(name, parent=parent)
        self.parameter_dials = []
        self.par = parent

        layout = QVBoxLayout()
        for parameter in parameters:
            widget = ParameterSpinBox(parent, parameter)
            self.parameter_dials.append(widget)
            layout.addWidget(widget)
            layout.addSpacing(-25)
        layout.addSpacing(25)
        self.setLayout(layout)

class ParameterContainer(QGroupBox):
    def __init__(self, name, parent):
        super(ParameterContainer, self).__init__(name, parent=parent)

        self.par = parent

        audio = ['THRESHOLD', 'RECORDING_LENGTH', 'DETECTION_SAMPLE_SIZE']
        self.audio_parameters = ParameterGroup('Audio Parameters', self.par, audio)

        image = ['SPECTROGRAM_LOW', 'SPECTROGRAM_HIGH', 'FREQUENCY_BANDS',
                'TIMESTEPS', 'FFT_LENGTH']
        self.image_parameters = ParameterGroup('Spectrogram Parameters', self.par, image)
        self.setFixedHeight(400)
        self.setFixedWidth(480)
        layout = QVBoxLayout()
        layout.addWidget(self.audio_parameters)
        layout.addWidget(self.image_parameters)
        self.setLayout(layout)

            
class MainWidget(QWidget):
    def __init__(self, parent):
        super(MainWidget, self).__init__(parent=parent)
        self.par = parent
        self.create_layout()

    def create_layout(self):
        
        # Parameters
        self.parameter_widget = ParameterContainer('Parameters', self)
        self.sample_widget = SampleWidget('Sample Display', self, config.audio_config)
        self.dataset_view = DatasetWidget(self.par, self)
        self.model_view = ModelView(self.par, self)
        
        # Layout


        # 
        layout = QGridLayout()
        layout.addWidget(self.dataset_view, 1, 1, 2, 1)
        layout.addWidget(self.sample_widget, 1, 2, 2, 1)
        layout.addWidget(self.parameter_widget, 1, 3, 1, 1)
        layout.addWidget(self.model_view, 2, 3, 1, 1)
        layout.setColumnMinimumWidth(1, 600)
        self.setLayout(layout)

    def global_sample(self, sample):
        self.sample_widget.new_sample(sample)
        self.sample_widget.recording_ready(True)

    def parameter_changed(self, parameter):
        attrs = ['THRESHOLD', 'TIMESTEPS', 'DETECTION_SAMPLE_SIZE',
                      'SPECTROGRAM_LOW', 'SPECTROGRAM_HIGH', 'FREQUENCY_BANDS',
                      'TIMESTEPS', 'FFT_LENGTH']
        for attr in attrs:
            print(attr, config.get(attr))
        if parameter == 'THRESHOLD':
            self.sample_widget.tline.setValue(config.THRESHOLD)
            self.sample_widget.tline2.setValue(-config.THRESHOLD)
        else:
            self.sample_widget.display_update()


class SampleWidget(QGroupBox, AudioIO):
    def __init__(self, name, parent, config):
        QGroupBox.__init__(self, parent=parent)
        AudioIO.__init__(self, **config)
        self.par = parent

        self.timer = QTimer()
        self.record_timer = QTimer()

        self.tracker = QSlider(Qt.Horizontal)
        self.tracker.setValue(0)
        self.tracker.setRange(0, self.n_chunks)

        self.sample_display = pg.PlotWidget()
        # self.sample_display.setYRange(-50000, 50000)
        
        self.line = pg.InfiniteLine(pen='g')
        self.sample_display.addItem(self.line)

        self.tline = pg.InfiniteLine(angle=0, pen='g')
        self.tline2 = pg.InfiniteLine(angle=0, pen='g')
        self.sample_display.addItem(self.tline)
        self.sample_display.addItem(self.tline2)

        self.tracker.valueChanged[int].connect(self.seek)
        self.tracker.valueChanged[int].connect(self.line_update)
        
        self.image_view = pg.ImageView()
        self.image_view.ui.menuBtn.hide()
        self.image_view.ui.roiBtn.hide()
        self.tiline = pg.InfiniteLine(angle=90, pen='g')
        self.image_view.addItem(self.tiline)
        self.seek(0)
        self.buttons = PlayToolbar(self)
        self.recording_ready(False)
        self.set_layout()

    def set_layout(self):

        self.sample_display.setBackground(None)
        steps = np.array([0.0, 0.2, 0.6, 1.0])
        colors = ['k', 'b', 'g', 'w']
        colormap = pg.ColorMap(steps, np.array([pg.colorTuple(pg.Color(c)) for c in colors]))
        self.image_view.setColorMap(colormap)

        layout = QGridLayout()
        layout.addWidget(self.sample_display, 1, 1, 1, 1)
        layout.addWidget(self.buttons, 2, 1, 1, 1)
        layout.addWidget(self.tracker, 3, 1, 1, 1)
        layout.addWidget(self.image_view, 4, 1, 1, 1)
        layout.setRowMinimumHeight(4, 200)
        layout.setRowMinimumHeight(1, 140)
        self.setLayout(layout)

    def update_spectrogram(self, image):
        image = np.flip(image.T)[::-1]
        self.image_view.setImage(image)
        
    def update_sample_display(self, data):
        # data = np.abs(data)
        self.sample_display.getPlotItem().plot(clear=True).setData(data)
        maxval = max([np.abs(data).max(), config.THRESHOLD])
        self.sample_display.setYRange(-maxval, maxval)
        self.sample_display.addItem(self.line)
        self.sample_display.addItem(self.tline)
        self.sample_display.addItem(self.tline2)
        self.tline.setValue(config.THRESHOLD)
        self.tline2.setValue(-config.THRESHOLD)
        self.seek(0)

    def seek(self, value):
        self.current_chunk = value
        self.tracker.setValue(self.current_chunk)

    def line_update(self, value):

        try: ln = len(self.current_sample.wave)
        except: ln = 0
        self.line.setValue(value/self.n_chunks*ln)
        self.tiline.setValue(round(value*config.TIMESTEPS/self.n_chunks))

    def display_update(self, sample=None, all=True):
        print('im caleed')
        if all:
            self.update_spectrogram(self.current_sample.create_spectrogram())
            self.update_sample_display(self.current_sample.wave)
        else:
            self.update_sample_display(sample)
        
        print('playing sample')

    ### Looping methods

    def start_monitoring(self, val):
        if val:
            print('monitor')
            self.monitoring = val
            self.timer.timeout.connect(self.monitor)
            self.timer.start(1)

        else:
            print('mon off')
            self.monitoring = val
            self.timer.stop()
            self.timer = QTimer()

    def start_recording(self, val):
        self.recording = val

    def play(self, val):
        if val:
            if self.monitoring:
                self.stop_button.click()
            print('play')
            self.playing = True
            self.timer.timeout.connect(self.play_chunk)
            self.timer.start(1)

        else:
            print('pause')
            self.playing = False
            self.timer.stop()
            self.timer = QTimer()

    def recording_ready(self, val):
        self.buttons.rec_button.setEnabled(val)
        self.buttons.play_button.setEnabled(val)

    def stop(self):
        print('stop')
        self.timer.stop()
        self.timer = QTimer()
        self.current_chunk = 0
        self.seek(self.current_chunk)

    def manage_buttons(self):
        print('manage_buttons')
        if not self.playing:
            self.buttons.play_button.click()

    def record_sample(self):
        t0 = time.time()
        data, raw = self.record(config.RECORDING_LENGTH)

        self.current_sample = self.par.dataset_view.new_sample(
            wave=data, 
            bytestring=raw, 
            save=True)

        self.display_update()

        y = 0
        self.time_taken = time.time() - t0
        print(self.time_taken)
        

class PlayToolbar(QGroupBox):
    def __init__(self, parent):
        super(PlayToolbar, self).__init__(parent=parent)
        self.par = parent
        self.play_button = ToggleButton(
            parent=self.par, 
            names=['Play', 'Pause', 'Play Disabled'], 
            trigger='play', 
            status=['Play Sample','Pause Sample'])

        self.loop_button = ToggleButton(
            parent=self.par, 
            names=['Loop', 'Loop Stop'], 
            trigger='loop',
            status=['Loop Sample', 'Stop Looping'])

        self.rec_button = ToggleButton(
            parent=self.par, 
            names=['Record', 'Record Stop', 'Record Disabled'], 
            trigger='start_recording',
            status=['Record', 'Stop Recording'])
        self.rec_button.setStatusTip('Select Dataset First')

        self.mon_button = ToggleButton(
            parent=self.par, 
            names=['Monitor', 'Stop Monitoring'], 
            trigger='start_monitoring',
            status=['Monitor', 'Stop Monitoring'])

        self.stop_button = ClickButton(
            parent=self.par, 
            name='Stop', 
            triggers=[self.par.stop, self.play_button.stop, self.rec_button.stop, self.mon_button.stop],
            status='Stop Playback')

        self.next_button = ClickButton(
            parent=self.par, 
            name='Next', 
            triggers=['pause'],
            status='Next Sample')
        
        self.prev_button = ClickButton(
            parent=self.par, 
            name='Previous', 
            triggers=['pause'],
            status='Previous Sample')

        self.play_all_button = ToggleButton(
            parent=self.par, 
            names=['Play All', 'Play Single'], 
            trigger='play_all',
            status=['Play All Samples', 'Play Single Sample'])
        
        self.classify_button = ToggleButton(
            parent=self.par, 
            names=['Classify', 'Classify Stop', 'Classify Disabled'], 
            trigger='start_monitoring',
            status=['Classify New Recordings', 'Stop Classifying'])
        self.classify_button.setEnabled(False)
        
        layout = QHBoxLayout()
        layout.addWidget(self.prev_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.next_button)
        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addSpacerItem(verticalSpacer)
        layout.addWidget(self.mon_button)
        layout.addWidget(self.rec_button)
        layout.addWidget(self.classify_button)
        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addSpacerItem(verticalSpacer)
        layout.addWidget(self.loop_button)
        layout.addWidget(self.play_all_button)
        self.setLayout(layout)

class DataToolbar(QGroupBox):
    def __init__(self, parent):
        super(DataToolbar, self).__init__(parent=parent)
        self.par = parent

        self.new_dataset_button = ClickButton(
            parent=self.par, 
            name='New Dataset', 
            triggers=[],
            status='New Dataset')

        self.del_dataset_button = ClickButton(
            parent=self.par, 
            name='Delete Dataset', 
            triggers=['del_dataset'],
            status='Delete Dataset')

        self.new_label_button = ClickButton(
            parent=self.par, 
            name='New Label', 
            triggers=['new_label'],
            status='New Label')

        self.del_label_button = ClickButton(
            parent=self.par, 
            name='Delete Label', 
            triggers=['del_label'],
            status='Delete Label')


        layout = QHBoxLayout()
        layout.addWidget(self.new_dataset_button)
        layout.addWidget(self.del_dataset_button)
        layout.addWidget(self.new_label_button)
        layout.addWidget(self.del_label_button)
        self.setLayout(layout)

class ModelToolbar(QGroupBox):
    def __init__(self, parent):
        super(ModelToolbar, self).__init__(parent=parent)
        self.par = paren

        self.new_dataset_button = ClickButton(
            parent=self.par, 
            name='New Dataset', 
            triggers=[],
            status='New Dataset')

        self.del_dataset_button = ClickButton(
            parent=self.par, 
            name='Delete Dataset', 
            triggers=['del_dataset'],
            status='Delete Dataset')

        self.new_label_button = ClickButton(
            parent=self.par, 
            name='New Label', 
            triggers=['new_label'],
            status='New Label')

        self.del_label_button = ClickButton(
            parent=self.par, 
            name='Delete Label', 
            triggers=['del_label'],
            status='Delete Label')


        layout = QHBoxLayout()
        layout.addWidget(self.new_dataset_button)
        layout.addWidget(self.del_dataset_button)
        layout.addWidget(self.new_label_button)
        layout.addWidget(self.del_label_button)
        self.setLayout(layout)


class DatasetWidget(QGroupBox, Dataset):
    def __init__(self, parent, main_widget):
        QGroupBox.__init__(self, parent=parent)
        Dataset.__init__(self, name='trash', existing=True)
        self.par = parent
        self.main_widget = main_widget

        self.dataset_path = self.audio_dir

        self.new_label_box = ActionComboBox(self.par, [MidiAction(parent=self.par)])
        self.new_label_button = ActionButton(self.par, self.par.nl, 'New Label')
        self.file_browser = FileBrowser(self.par, self)
        
        self.dataset_selection = DirectoryComboBox(self.par, config.AUDIO, 'Select Dataset:', 'NewDataset',['new_dataset', 'del_dataset'])
        self.dataset_selection.selection.activated[str].connect(self.change_dataset)

        self.label_selection = DirectoryComboBox(self.par, config.AUDIO, 'Select Label:', 'Label', ['new_label','del_label'])
        self.label_selection.selection.activated[str].connect(self.change_label)
        self.label_selection.setEnabled(False)

        self.toolbar = DataToolbar(self)

        self.set_layout()

    def set_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.dataset_selection)
        layout.addSpacing(-25)
        layout.addWidget(self.label_selection)
        layout.addSpacing(-25)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.file_browser)
        # layout.addWidget(self.new_label_button)
        # layout.addWidget(self.new_label_box)
        self.setLayout(layout)

    def change_dataset(self, path):
        self.name = path
        path = os.path.join(config.AUDIO, path)
        self.file_browser.set_path(path)
        self.dataset_path = self.audio_dir = path
        self.load_existing()
        self.par.statusBar().showMessage('Loaded dataset {}'.format(path))
        self.label_selection.set_path(path)
        self.label_selection.setEnabled(True)
        print(self.summary())

    def change_label(self, label):
        path = os.path.join(config.AUDIO, self.dataset_path, label)
        self.current_label = label
        self.file_browser.set_path(path)
        self.file_browser.setCurrentIndex(-1)
        self.file_browser.DoubleClicked()

    def sample_selected(self, sample_no):
        sample = self.current_sample_id = self.get_sample(sample_no-1)
        self.current_sample_id = sample_no
        self.main_widget.global_sample(sample)

    def get_next_sample(self):
        try:
            return self.get_sample(self.current_sample_id+1)
        except:
            pass
        
    def get_previous_sample(self):
        try:
            return self.get_sample(self.current_sample_id-1)
        except:
            pass

    def new_label(self):
        pass

    def new_dataset(self):
        pass

    def del_dataset(self):
        pass

    def del_label(self):
        pass


class FileBrowser(QTreeView):
    def __init__(self, parent, datawidget):
        super(FileBrowser, self).__init__(parent=parent)
        self.par = parent
        self.data_widget = datawidget
        self.sample_no = -1

        self.model = QFileSystemModel()
        self.setModel(self.model)
        self.setAnimated(False)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.set_path(config.AUDIO)

    def set_path(self, directory):
        self.setRootIndex(self.model.index(directory))
        # self.clicked.connect(self.select_sample_in_dataset)
        # self.currentChanged.connect(print('changed'))
        self.selectionModel().selectionChanged.connect(self.select_sample_in_dataset)
        self.model.setRootPath(directory)
        

    def select_sample_in_dataset(self, item):
        # QItemSelection().value
        # QItemSelectionRange().indexes()
        # QModelIndex().data(0)
        # print( item.row(), item.data())
        item = item.value(0).indexes()[0].data(0)
        sample_no, ext = item.split('.')
        if 'wav' in ext and sample_no!=self.sample_no:
            self.sample_no = sample_no
            self.data_widget.sample_selected(
                sample_no=int(sample_no))

        # self.label_selection.clear()
        # self.label_selection.addItems(self.dataset.hashmap.keys())
        # self.label_selection.setEnabled(True)
        # self.create_label_button.setEnabled(True)

    
# class 

class DirectoryComboBox(QWidget):
    def __init__(self, parent, directory, name, icon, triggers):
        super(DirectoryComboBox, self).__init__(parent=parent)
        self.par = parent
        self.icon = icon
        self.name = name
        self.fsm  = QFileSystemModel()
        self.selection = QComboBox()
        self.set_path(directory)

        self.label = QLabel(name)
        self.label.setFixedWidth(120)
        # self.label.setPixmap(QPixmap(get_icon(self.icon)))
        self.label.setText(name)
        
        ic = QLabel()
        ic.setPixmap(QPixmap(get_icon(self.icon)))
        ic.setFixedWidth(30)

        self.new_button = ClickButton(
            parent=self.par, 
            name='New', 
            triggers=[triggers[0]],
            status='New')
        self.new_button.setFixedWidth(30)

        self.del_button = ClickButton(
            parent=self.par, 
            name='Delete', 
            triggers=[triggers[1]],
            status='Delete')
        self.del_button.setFixedWidth(30)

        layout = QHBoxLayout()
        layout.addWidget(ic)
        layout.addWidget(self.label)
        layout.addWidget(self.selection)
        layout.addWidget(self.new_button)
        layout.addWidget(self.del_button)
        self.setLayout(layout)

    def set_path(self, directory):
        index = self.fsm.setRootPath(directory)
        self.selection.setModel(self.fsm)
        self.selection.setRootModelIndex(index)
        icon = QIcon(QPixmap(get_icon(self.icon)))
        self.selection.insertItem(0, icon, self.name)
        self.selection.setCurrentIndex(0)

    def check_existing(self, value):
        return True if self.selection.findData(value) >= 0 else False

class LabeledComboBox(QWidget):
    def __init__(self, parent, label, items, selection='Default'):
        super(LabeledComboBox, self).__init__(parent=parent)
        self.label = QLabel(label)

        self.combo = QComboBox()
        self.combo.addItems(items)
        icon = QIcon(QPixmap(get_icon(selection)))
        self.combo.insertItem(0, icon, label)
        self.combo.model().item(0).setEnabled(False)
        self.combo.setCurrentIndex(0)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.combo)
        self.setLayout(layout)

class SettingsMenu(QWidget):
    def __init__(self, audio_object):
        super(SettingsMenu, self).__init__()
        self.setWindowTitle('Settings Menu')
        _, list = audio_object.get_device_info()
        self.devices = LabeledComboBox(self, 'Audio devices: ', list)


class ModelView(QGroupBox):
    def __init__(self, parent, main_widget):
        super(ModelView, self).__init__(parent=parent)
        self.par = main_widget

        models = ['Retarded Classifier']
        self.classifier_selection = LabeledComboBox(self, 'Select Classifier: ', models, 'Classifier')
        
        self.model_selection = DirectoryComboBox(self.par, config.AUDIO, 'Select Model:', 'New Model',['new_model', 'new_dataset'])
        self.model_selection.set_path(config.MODELS)
        layout = QVBoxLayout()
        layout.addWidget(self.classifier_selection)
        layout.addWidget(self.model_selection)
        self.setLayout(layout)


