from PySide2 import QtCore, QtWidgets, QtGui
import sys, random, os, time
import numpy as np
from ml_midi.processing import Dataset
import ml_midi.config as config


class ModelView(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ModelView, self).__init__(parent=parent)
        self.label = '0'
        self.parent = parent
        self.dataset_name = 'new'
        self.dataset = None
        self.model = None
        self.setup()

    def new_dataset(self):
        text, okPressed = QtWidgets.QInputDialog.getText(self, "New dataset","Name:", QLineEdit.Normal, "")
        if okPressed and text != '':
            dataset = Dataset(text)
            self.dataset = dataset
            self.update_summary()
            return dataset

    def get_dataset(self):
        dataset = Dataset(self.dataset_name)
        self.dataset = dataset
        self.update_summary()
        return dataset

    def update_summary(self):
        self.dataset_summary.setPlainText(self.dataset.summary())

    def setup(self):

        group = QtWidgets.QGroupBox('Images')
        self.layout = QtWidgets.QGridLayout()

        layout = QtWidgets.QVBoxLayout()
        group.setLayout(layout)
        self.layout.addWidget(group)

        self.image_dataset_button = QtWidgets.QPushButton()
        self.image_dataset_button.setText('Create image dataset')
        self.image_dataset_button.clicked.connect(self.create_images)
        
        # layout.addWidget(self.w_label) #, 1, 2, 1, 1)
        layout.addWidget(self.image_dataset_button)#, 2, 2, 1, 1)

        self.setLayout(self.layout)

    def change_dataset(self, name):
        self.dataset_name = name
        dataset = Dataset(self.dataset_name)
        self.dataset = self.parent.dataset = dataset

        self.label_selection.addItems(self.dataset.hashmap.keys())
        self.label_selection.setEnabled(True)
        # self.label_selection.setCurrentText('Select label...')

        self.model = QtGui.QFileSystemModel()
        directory = os.path.join(config.DATA, 'audio', name, self.dataset.current_label)
        self.model.setRootPath(directory)
        # index = model.setRootPath(directory)
        self.sample_tree.setModel(self.model)
        self.sample_tree.setRootIndex(self.model.index(directory))
        self.model.setRootPath(directory)
        self.sample_tree.doubleClicked.connect(self.play_sample)
        # self.sample_tree.setRootModelIndex(index)
        
        self.sample_tree.setAnimated(False)
        self.sample_tree.setIndentation(20)
        self.sample_tree.setSortingEnabled(True)
        # self.label_selection.setModel(fsm)
        # self.label_selection.setRootModelIndex(index)


        self.update_summary()

    def change_label(self, label):
        self.label = label
        self.dataset.current_label = label

    def play_sample(self, item):
        sample_no, ext = item.data().split('.')
        if 'wav' in ext:
            self.parent.sample_selected(
                sample_no=int(sample_no))

    def new_label(self):
        pass

    def new_dataset(self):
        pass
        # QtCore.QModelIndex().

    def create_images(self):
        pass