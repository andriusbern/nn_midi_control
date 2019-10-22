from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import pyqtgraph as pg
from .actions import *
from ml_midi.processing import Dataset, DataSample, AudioIO, Midi
import os, time, shutil
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
    def __init__(self, parent, names, trigger, status=None, own_trigger=False):
        super(ToggleButton, self).__init__(parent=parent)
        self.par = parent
        self.setCheckable(True)
        self.names = names
        self.status = status
        self.status_change(False)
        if own_trigger:
            self.clicked[bool].connect(getattr(self.par, trigger))
        else:
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
        # self.label.setFont(QFont(7, QFont.Bold))
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
        self.output_view = OutputView(self)
        

        tabs = QTabWidget()
        tabs.addTab(self.dataset_view, 't1')
        tabs.setTabText(0, 'Audio Datasets')
        tabs.addTab(QWidget(), 't2')
        tabs.setTabText(1, 'Image Datasets')

        # Layout
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.output_view)
        self.scroll.setWidgetResizable(True)
        # self.scroll.setSizeIncrement(100, 100)
        # self.scroll.set
        layout = QGridLayout(self)
        layout.addWidget(tabs, 1, 1, 2, 1)
        layout.addWidget(self.sample_widget, 1, 2, 3, 1)
        layout.addWidget(self.parameter_widget, 1, 3, 1, 1)
        layout.addWidget(self.scroll, 2, 3, 2, 1)
        layout.addWidget(self.model_view, 3, 1, 1, 1)
        layout.setColumnMinimumWidth(1, 500)
        layout.setRowMinimumHeight(3, 300)

    def global_sample(self, sample):
        self.sample_widget.new_sample(sample)
        self.sample_widget.recording_ready(True)

    def label_selected(self, label):
        self.sample_widget.recording_ready(True)
        self.output_view.set_active(label)

    def dataset_selected(self):
        del self.output_view
        self.output_view = OutputView(self)
        labels = self.dataset_view.labels
        n_samples = [x for x in range(len(labels))] #[self.dataset_view.samples_per_label[label] for label in labels]
        self.output_view.create_labels(labels, n_samples)
        self.scroll.setWidget(self.output_view)
        

    def parameter_changed(self, parameter):
        attrs = ['THRESHOLD', 'TIMESTEPS', 'DETECTION_SAMPLE_SIZE',
                      'SPECTROGRAM_LOW', 'SPECTROGRAM_HIGH', 'FREQUENCY_BANDS',
                      'TIMESTEPS', 'FFT_LENGTH']
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
        self.image_view.getView().getViewBox().setBackground(None)
        self.image_view.getHistogramWidget().setBackground(None)
        self.tiline = pg.InfiniteLine(angle=90, pen='g')
        self.image_view.addItem(self.tiline)
        self.seek(0)
        self.buttons = PlayToolbar(self)
        self.recording_ready(False)
        self.volumebar = VolumeWidget(self)
        self.set_layout()

    def set_layout(self):

        self.sample_display.setBackground(None)
        steps = np.array([0.1, 0.4, 0.7, 1.0])
        colors = ['k', 'b', 'g', 'w']
        colormap = pg.ColorMap(steps, np.array([pg.colorTuple(pg.Color(c)) for c in colors]))
        self.image_view.setColorMap(colormap)

        layout = QGridLayout()
        layout.addWidget(self.sample_display, 1, 1, 1, 1)
        layout.addWidget(self.volumebar, 1, 2, 1, 1)
        layout.addWidget(self.buttons, 2, 1, 1, 2)
        layout.addWidget(self.tracker, 3, 1, 1, 2)
        layout.addWidget(self.image_view, 4, 1, 1, 2)
        layout.setRowMinimumHeight(4, 400)
        layout.setRowMinimumHeight(1, 140)
        self.setLayout(layout)

    def update_spectrogram(self, image):
        image = np.flip(image.T)[::-1]
        self.image_view.setImage(image, autoRange=True, autoLevels=True, autoHistogramRange=False)
        self.image_view.setLevels(0, 100)
        # self.image_view.getHistogramWidget().setRange(0, 100)
        
    
        
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
        if all:
            self.update_spectrogram(self.current_sample.create_spectrogram())
            self.update_sample_display(self.current_sample.wave)
        else:
            self.update_sample_display(sample)
        

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
                self.buttons.stop_button.click()
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
            triggers=['new_label_dialog'],
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

        # self.new_label_button = ActionButton(self.par, self.par.nl, 'New Label')
        
        self.file_browser = FileBrowser(self.par, self)
        
        self.dataset_selection = DirectoryComboBox(self, config.AUDIO, 'Dataset:', 'NewDataset',['new_dataset', 'del_dataset'])
        self.dataset_selection.selection.activated[str].connect(self.change_dataset)

        self.label_selection = DirectoryComboBox(self, config.AUDIO, 'Label:', 'Label', ['new_label_dialog','del_label'])
        self.label_selection.selection.activated[str].connect(self.change_label)
        self.label_selection.setEnabled(False)

        self.toolbar = DataToolbar(self)

        self.set_layout()

    def set_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.dataset_selection)
        # layout.addSpacing(-25)
        layout.addWidget(self.label_selection)
        # layout.addSpacing(-25)
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
        self.label_selection.setEnabled(True)
        self.label_selection.set_path(path)
        # self.label_selection.selection.setCurrentIndex(0)
        label = self.label_selection.selection.itemText(0)
        self.change_label(label)
        print(self.summary())
        self.main_widget.dataset_selected()

    def change_label(self, label):
        path = os.path.join(self.audio_dir, label)
        self.current_label = label
        self.file_browser.set_path(path)
        self.main_widget.label_selected(label)
        # index = self.label_selection.selection.model().index(0,0)
        # self.label_selection.selection.
        # self.label_selection.selection.setCurrentText(label)
        # self.label_selection.selection.setCurrentIndex(self.label_selection.selection.findData(label))
        # self.file_browser.setCurrentIndex(-1)
        # self.file_browser.DoubleClicked()

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

    def new_label_dialog(self):
        label, ok_pressed = NewDialog(self, 'label', '').ask()
        if ok_pressed and label != '':
            self.new_label(label)
            self.change_label(label)
            self.label_selection.set_path(os.path.join(self.audio_dir, label))
            self.label_selection.selection.setCurrentText(label)
            self.main_widget.output_view.new_label(label)

    def new_dataset(self):
        name, ok_pressed = NewDialog(self, 'dataset', '').ask()
        if ok_pressed and name != '':
            self.create_new(name)
            self.change_dataset(self.audio_dir)
            self.dataset_selection.selection.setCurrentText(name)

    def del_dataset(self):
        reply = DeleteMessage(self, self.name, 'dataset') .ask()
        if reply == QtWidgets.QMessageBox.Yes:
            shutil.rmtree(self.audio_dir)
            self.dataset_selection.set_path(self.audio_dir)
            self.dataset_selection.selection.setCurrentIndex(0)

    def del_label(self):
        reply = DeleteMessage(self, self.current_label, 'label').ask()
        if reply == QtWidgets.QMessageBox.Yes:
            path = os.path.join(self.audio_dir, self.current_label)
            shutil.rmtree(path)
            self.file_browser.set_path(self.audio_dir)
            self.main_widget.output_view.del_label(self.current_label)

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
            triggers=[getattr(self.par,triggers[0])],
            status='New')
        self.new_button.setFixedWidth(30)

        self.del_button = ClickButton(
            parent=self.par, 
            name='Delete', 
            triggers=[getattr(self.par,triggers[1])],
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
        self.par = parent
        self.main_widget = main_widget
        self.setTitle('Models')

        models = ['Retarded Classifier']
        self.classifier_selection = LabeledComboBox(self, 'Select Classifier: ', models, 'Classifier')
        
        self.model_selection = DirectoryComboBox(self, config.AUDIO, 'Select Model:', 'New Model',['new_model', 'del_model'])
        self.model_selection.set_path(config.MODELS)

        # self.new_output = ActionComboBox(self.par, [MidiAction(parent=self.par)])

        layout = QVBoxLayout()
        layout.addWidget(self.classifier_selection)
        layout.addWidget(self.model_selection)
        self.setLayout(layout)

    def new_model(self):
        pass

    def del_model(self):
        pass


class DeleteMessage(QMessageBox):
    def __init__(self, parent, name, objectname):
        super(DeleteMessage, self).__init__()
        self.par = parent
        self.objectname = objectname
        self.name = name

    def ask(self):

        reply = self.question(
            self.par, 
            'Delete {}?'.format(self.objectname), 
            'Permanently delete {} "{}"?'.format(self.objectname, self.name), 
            QtWidgets.QMessageBox.Yes, 
            QtWidgets.QMessageBox.No)
        return reply

class NewDialog(QInputDialog):
    def __init__(self, parent, name, objectname):
        super(NewDialog, self).__init__()
        self.par = parent
        self.objectname = name
        # self.reply = self.question(
        #     parent, 
        #     'Delete {}?'.format(objectname), 
        #     'Permanently delete {} "{}"?'.format(objectname, name), 
        #     QtWidgets.QMessageBox.Yes, 
        #     QtWidgets.QMessageBox.No)

    def ask(self):
        text, okPressed = self.getText(
            self.par,
            'New {}'.format(self.objectname),
            'New {} name: '.format(self.objectname),
            QtWidgets.QLineEdit.Normal, "")

        return text, okPressed
        
        # self.Question()
        # self.raise_()
        # self.show()
    
class VolumeWidget(QGroupBox):
    def __init__(self, parent):
        super(VolumeWidget, self).__init__()
        self.par = parent
        self.slider = QSlider(Qt.Vertical)
        self.slider.setRange(0, 100)
        self.slider.valueChanged.connect(self.changed)
        self.slider.setValue(self.par.volume)

        self.prev_vol = self.par.volume
        ic = QLabel()
        ic.setPixmap(QPixmap(get_icon('Volume')))

        button = ToggleButton(
            self, 
            names=['Mute', 'Unmute'],
            trigger='mute',
            status=['Mute', 'Unmute'], 
            own_trigger=True)
        button.setFixedWidth(20)

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(button)
        self.setLayout(layout)

    def changed(self, val):
        self.par.volume = val

    def mute(self, val):
        if val:
            self.prev_vol = self.par.volume
            self.par.volume = 0
            self.slider.setValue(0)
        else:
            self.par.volume = self.prev_vol
            self.slider.setValue(self.prev_vol)


### OUTPUTS

class NewOutputWidget(QComboBox):
    def __init__(self, parent):
        super(NewOutputWidget, self).__init__()

        self.par = parent
        # self.action_list = actions
        self.options = ['Midi', 'Audio']

        icon = QIcon(QPixmap(get_icon('Default')))
        self.insertItem(0, icon, 'New output')
        self.model().item(0).setEnabled(False)

        self.activated.connect(self.selection)
        self.add_options()

    def selection(self):
        """
        Trigger an action based on selection
        """
        self.currentIndex()
        self.action_list[self.currentIndex()-1].trigger()
        self.setCurrentIndex(0)

    def add_options(self):
        for option in self.options:
            icon = QIcon(QPixmap(get_icon('Default')))
            self.addItem(icon, option)



class OutputGroup(QWidget):
    def __init__(self, parent, name):
        QWidget.__init__(self, parent=parent)
        # Midi.__init__(self)
        self.par = parent
        self.label = QLabel('Label: {}'.format(name))
        self.lay = QHBoxLayout(self)
        self.lay.addWidget(self.label)

    def configure(self):
        pass

    def send(self):
        pass

class MidiOutput(OutputGroup):
    def __init__(self, parent):
        super(MidiOutput, self).__init__()

    def configure(self):
        pass

    def send(self):
        pass
        

class LED(QLabel):
    def __init__(self, parent):
        super(LED, self).__init__()



class OutputView(QGroupBox, Midi):
    def __init__(self, parent):
        super(OutputView, self).__init__(parent=parent)

        self.par = parent
        self.setTitle('Outputs')
        self.lay = QVBoxLayout(self)
        self.lay.setSpacing(0)
        self.lay.setContentsMargins(0,0,0,0)
        self.labels = []
        self.label_map = {}

    def create_labels(self, labels, n_samples):
        for i, label in enumerate(labels):
            lab = LabelGroup(self.par, label, self, n_samples[i])
            self.labels.append(lab)
            self.label_map[label] = lab
            self.lay.addWidget(lab)
            # self.lay.addSpacing(-100)
        self.lay.insertStretch(-1, 1)

    def set_active(self, label):
        try:
            [x.label_row.set_active(False) for x in self.labels]
            active = self.label_map[label]
            active.label_row.set_active(True)
        except:
            pass
        
    def new_label(self, label):
        lab = LabelGroup(self.par, label, self)
        self.lay.addWidget(lab)
        self.labels.append(lab)
        self.label_map[label] = lab
        self.lay.insertStretch(-1, 1)

    def del_label(self, label):
        lab = self.label_map[label]
        self.lay.removeWidget(lab)
        self.labels.remove(lab)
        self.label_map.pop(label)
        del lab


class LabelRow(QWidget):
    def __init__(self, parent, name, n_samples=0):
        super(LabelRow, self).__init__(parent=parent)

        self.par = parent
        self.setAutoFillBackground(True)
        self.name = name
        self.counter = None
        self.n_samples = n_samples
        self.toggle = ToggleButton(
            parent=self.par, 
            names=['Outputs', 'Outputs Off'], 
            trigger='expand',
            status=['Show Outputs', 'Hide Outputs'],
            own_trigger=True)
        self.toggle.setFixedWidth(30)

        self.activate_btn = ToggleButton(
            parent=self, 
            names=['Active', 'Inactive'], 
            trigger='label_select',
            status=['Activate', 'Deactivate'],
            own_trigger=True)
        self.activate_btn.setFixedWidth(30)

        self.label = QPushButton('Label: {:10}'.format(name))
        self.label.setEnabled(False)
        self.count = QPushButton('Samples: {:10}'.format(n_samples))

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.activate_btn)
        self.layout.addWidget(self.toggle)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.count)
        # self.layout.addWidget()

    def label_select(self):
        self.par.select_label(self.name)

    def set_active(self, val):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.green if val else Qt.black)
        self.setPalette(palette)
        self.activate_btn.setChecked(val)


class LabelGroup(QWidget):
    def __init__(self, parent, name, output_widget, n_samples):
        super(LabelGroup, self).__init__(parent=parent)

        self.par = parent
        self.output_widget = output_widget
        self.name = name
        self.led = None
        self.n_samples = n_samples

        self.new_output_row = NewOutputWidget(self)
        self.output_container = QGroupBox()
        self.output_layout = QVBoxLayout(self.output_container)
        self.output_layout.setSpacing(0)
        self.output_layout.setContentsMargins(0,0,0,0)
        self.outputs = ['Midi']
        self.output_objects = []
        self.output_map = {}
        self.output_container.setVisible(False)
        self.add_outputs()
        
        self.n_outputs = None
        self.label_row = LabelRow(self, name, n_samples)
        
        self.lay = QVBoxLayout(self)
        self.lay.addWidget(self.label_row)
        self.lay.addWidget(self.output_container)
        self.lay.insertStretch(-1, 1)

    def trigger_outputs(self, label):
        for output in self.outputs:
            output.send()

    @QtCore.Slot()
    def expand(self, state):
        self.output_container.setVisible(state)

    def add_outputs(self):
        for output in self.outputs:
            out = OutputGroup(self, output)
            self.output_objects.append(out)
            
            self.output_layout.addWidget(out)
        self.output_layout.addWidget(self.new_output_row)
        self.output_layout.insertStretch(-1, 1)
            
    def select_label(self, label):
        self.par.dataset_view.change_label(label)
        self.output_widget.set_active(label)
        

