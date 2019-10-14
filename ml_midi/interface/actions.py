from PySide2 import QtWidgets, QtGui, QtCore
import ml_midi.config as config
import os

class DefaultAction(QtWidgets.QAction):
    def __init__(self, parent, name):
        super(DefaultAction, self).__init__(parent)
        self.par = parent
        self.name = name
        self.setText(self.name)
        self.set_icon()
        # self.setIconVisibleInMenu = True
        self.setIconVisibleInMenu(True)
        self.assign_trigger()
        
    def set_icon(self, name=None):
        path = os.path.join(config.ICONS, self.name+'.svg')
        icon = QtGui.QIcon(parent=self)
        icon.addPixmap(QtGui.QPixmap(path))
    
        self.setIcon(icon)
    
    def assign_trigger(self):
        pass

class DefaultToggleAction(DefaultAction):
    def __init__(self, parent, name):
        super(DefaultToggleAction, self).__init__(parent=parent, name=name)
        self.setCheckable(True)
    


class MidiAction(DefaultAction):
    def __init__(self, parent, name='Midi'):
        super(MidiAction, self).__init__(parent=parent, name=name)

        self.setStatusTip('New midi action')
        self.triggered.connect(self.par.new_midi)

class RecordAction(DefaultToggleAction):
    def __init__(self, parent, name='Record'):
        super(RecordAction, self).__init__(parent=parent, name=name)

        self.setStatusTip('Start Recording')
        self.setToolTip('Record')
        self.toggled.connect(self.par.record_loop)

class SettingsAction(DefaultAction):
    def __init__(self, parent, name='Settings'):
        super(SettingsAction, self).__init__(parent=parent, name=name)
        self.triggered.connect(self.par.settings_menu)

class PlaySampleAction(DefaultToggleAction):
    def __init__(self, parent, name='Play'):
        super(PlaySampleAction, self).__init__(parent=parent, name=name)

        # self.
        self.setShortcut('CTRL+G')
        self.setStatusTip('Play Sample')
        # self.set_icon(names=['Play', 'Pause'])
        # self.toggled.connect(self.par.play_sample)
        self.toggled.connect(self.par.play_sample)
        # self.toggled.connect(self.par.pause)

class NewLabelAction(DefaultAction):
    def __init__(self, parent, name='Label'):
        super(NewLabelAction, self).__init__(parent=parent, name=name)

        self.setShortcut('CTRL+N')
        self.setStatusTip('New Label')
        self.triggered.connect(self.par.new_label)

# class SampleSelectionAction(DefaultAction):
