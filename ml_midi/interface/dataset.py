from PyQt5 import QtCore, QtWidgets, QtGui
import sys, random, os, time, shutil
import numpy as np
from ml_midi.processing import Dataset
import ml_midi.config as config


class DatasetView(QtWidgets.QWidget):
    def __init__(self, parent):
        super(DatasetView, self).__init__(parent=parent)
        self.label = '0'
        self.parent = parent
        self.dataset_name = 'new'
        self.dataset = None
        self.model = None
        self.setup()
    def new_dataset(self):
        text, okPressed = QtWidgets.QInputDialog.getText(self, "New dataset","Name:", QtWidgets.QLineEdit.Normal, "")
        if okPressed and text != '':
            print(self.dataset_selection.findData(text))
            if self.dataset_selection.findData(text) >= 0:
                self.dataset_summary.setPlainText('Dataset exists.')
            else:
                self.change_dataset(text, existing=False)
                self.update_dataset_index()
                index = self.dataset_selection.findText(text)
                self.dataset_selection.setCurrentIndex(index)
                self.parent.dataset_selected()
                self.update_summary()

    def delete_dataset(self):
        name = self.dataset.name
        reply = QtWidgets.QMessageBox.question(
            self, 
            'Delete dataset?', 
            'Permanently delete dataset {}?'.format(name), 
            QtWidgets.QMessageBox.Yes, 
            QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            path = self.dataset.audio_dir
            del self.dataset
            shutil.rmtree(path)
            self.update_dataset_index()
            self.label_selection.setEnabled(False)
            self.delete_dataset_button.setEnabled(False)
            index = self.dataset_selection.findText(name)
            self.dataset_selection.setCurrentIndex(index)
            self.dataset_summary.setPlainText('Removed {}'.format(name))

    def change_dataset(self, name, existing=True):
        self.dataset_summary.setPlainText('Loading dataset "{}..."'.format(name))
        self.dataset_name = name
        dataset = Dataset(self.dataset_name, existing=existing)
        self.dataset = dataset
        self.parent.dataset_selected()
        directory = os.path.join(config.DATA, 'audio', name, self.dataset.current_label)
        self.update_tree(directory)
        self.delete_dataset_button.setEnabled(True)
        self.update_summary()

    def change_label(self, label):
        self.label = label
        self.dataset.current_label = label
        directory = os.path.join(config.DATA, 'audio', self.dataset.name, self.dataset.current_label)
        self.update_tree(directory)

    def delete_sample(self):
        indexes = self.sample_tree.selectedIndexes
        self.dataset.remove
        os.remove()

    def delete_all_samples(self):
        pass



    def play_sample(self, item):
        sample_no, ext = item.data().split('.')
        if 'wav' in ext:
            self.parent.sample_selected(
                sample_no=int(sample_no))

    def new_label(self):
        text, okPressed = QtWidgets.QInputDialog.getText(self, "New Label","Name:", QtWidgets.QLineEdit.Normal, "")
        if okPressed and text != '':
            self.dataset.new_label(text)
            self.change_label(text)
            self.update_summary()

    def update_tree(self, directory):
        self.model = QtGui.QFileSystemModel()
        self.sample_tree.setModel(self.model)
        self.sample_tree.setRootIndex(self.model.index(directory))
        self.sample_tree.doubleClicked.connect(self.play_sample)
        self.model.setRootPath(directory)

        self.sample_tree.setAnimated(False)
        self.sample_tree.setIndentation(20)
        self.sample_tree.setSortingEnabled(True)
        self.label_selection.clear()
        self.label_selection.addItems(self.dataset.hashmap.keys())
        self.label_selection.setEnabled(True)
        self.create_label_button.setEnabled(True)

    def update_dataset_index(self):
        fsm = QtGui.QFileSystemModel()
        directory = os.path.join(config.DATA, 'audio')
        index = fsm.setRootPath(directory)
        self.dataset_selection.setModel(fsm)
        self.dataset_selection.setRootModelIndex(index)

    def update_summary(self):
        self.dataset_summary.setPlainText(self.dataset.summary())

    def setup(self):
        self.layout = QtWidgets.QGridLayout()

        group = QtWidgets.QGroupBox('Wave Datasets')
        
        self.layout = QtWidgets.QGridLayout()

        layout = QtWidgets.QGridLayout()
        group.setLayout(layout)
        self.layout.addWidget(group)

        self.label_category = QtWidgets.QLabel()
        self.label_category.setText('Label:')

        self.dataset_selection = QtWidgets.QComboBox()
        self.update_dataset_index()
        # self.dataset_selection.setCurrentText('Select dataset...')
        self.dataset_selection.activated[str].connect(
            self.change_dataset)

        self.create_dataset_button = QtWidgets.QPushButton()
        self.create_dataset_button.setText('New dataset')
        self.create_dataset_button.clicked.connect(self.new_dataset)

        self.delete_dataset_button = QtWidgets.QPushButton()
        self.delete_dataset_button.setText('Delete')
        self.delete_dataset_button.clicked.connect(self.delete_dataset)
        self.delete_dataset_button.setEnabled(False)

        self.sample_tree = QtWidgets.QTreeView()
        self.sample_tree.setWindowTitle("Sample View")

        self.delete_sample_button = QtWidgets.QPushButton()
        self.delete_sample_button.setText('Delete')
        self.delete_sample_button.clicked.connect(self.delete_sample)
        
        self.delete_all_samples_button = QtWidgets.QPushButton()
        self.delete_all_samples_button.setText('Delete')
        self.delete_all_samples_button.clicked.connect(self.delete_all_samples)

        self.label_selection = QtWidgets.QComboBox()

        # self.label_selection.setCurrentText('Select label...')
        self.label_selection.setEnabled(False)
        self.label_selection.activated[str].connect(
            self.change_label)

        self.create_label_button = QtWidgets.QPushButton()
        self.create_label_button.setText('Create new label')
        self.create_label_button.clicked.connect(self.new_label)
        self.create_label_button.setEnabled(False)
        
        self.dataset_label = QtWidgets.QLabel()
        self.dataset_label.setText('Dataset:')
        
        self.dataset_summary = QtWidgets.QPlainTextEdit()
        # self.dataset_summary.setFixedSize(250, 200)

        layout.addWidget(self.dataset_label, 1, 1, 1, 1)
        layout.addWidget(self.dataset_selection, 1, 2, 1, 1)
        layout.addWidget(self.create_dataset_button, 2, 1, 1, 1)
        layout.addWidget(self.delete_dataset_button, 2, 2, 1, 1)
        layout.addWidget(self.label_category, 3, 1, 1, 1)
        layout.addWidget(self.label_selection, 3, 2, 1, 1)
        layout.addWidget(self.create_label_button, 4, 1, 1, 2)
        layout.addWidget(self.dataset_summary, 7, 1, 1, 2)
        layout.addWidget(self.sample_tree, 1, 3, 7, 1)
        layout.setColumnMinimumWidth(3, 300)
        layout.setColumnMinimumWidth(2, 150)

        self.setLayout(self.layout)

class LabelTree(QtWidgets.QTreeView):
    def __init__(self, labelconf):
        pass

    def create_labels(self):
        pass

    def label_row(self):

        type = None # midi / audio
        



        


class FileTree(QtWidgets.QTreeView):
    def __init__(self):
        pass