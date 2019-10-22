import tensorflow as tf
import numpy as np
from ml_midi.config import ConfigManager as config
from random import shuffle
# from data_handler import DataIO, Dataset
from ml_midi.processing import DataIO, Dataset

class ConvNet(object):
    """
    Save net parameters in YAML files
    """
    def __init__(self, config):
        # self.dataset = Dataset('default')
        self.input = [20, 20]
        self.bins = 20
        self.n_labels = 1
        self.lr = 0.001
        self.config = config
        self.graph = tf.Graph()
        self.setup()
        self.session = tf.Session(graph=self.graph)
        self.session.run(self.init)

    def setup(self):
        with self.graph.as_default():
            self._placeholders()
            self._build_net()
            self.loss = tf.reduce_mean(tf.square(self.output - self.label_ph))
            self.train_op = tf.train.AdamOptimizer(self.lr).minimize(self.loss)
            self.init = tf.global_variables_initializer()

    def _placeholders(self):
        self.input_ph = tf.placeholder(tf.float32, shape=(None, self.input[0], self.input[1], 1,), name='input')
        self.label_ph = tf.placeholder(tf.float32, shape=(None, 4), name='output')
        
    def _build_net(self):
        """
        Build the network based on the network config parameters
        """
        output = tf.layers.conv2d(
            inputs=self.input_ph,
            filters=self.config['filters'][0],
            strides=self.config['strides'][0],
            kernel_size=self.config['kernel_size'][0],
            activation=tf.nn.relu,
            name='c0')

        for i, layer in enumerate(self.config['filters'][1:]):
            output = tf.layers.conv2d(
                inputs=output,
                filters=layer,
                strides=self.config['strides'][i+1],
                kernel_size=self.config['kernel_size'][i+1],
                activation=tf.nn.relu,
                name='c{}'.format(i+1))

        # Fully connected layers
        output = tf.layers.flatten(output)
        for i, layer in enumerate(self.config['fc_layers']):
            output = tf.layers.dense(
                output,
                layer,
                activation=tf.nn.relu,
                name='fc{}'.format(i))

        output = tf.layers.dense(
            output,
            4,
            activation=tf.nn.softmax,
            name='output')

        self.output = tf.squeeze(output)
        # self.init = tf.global_variables_initializer()
        # self.session = tf.Session(graph=self.graph)
        # self.session.run(self.init)

    def set_dataset(self):
        pass

    def train(self):
        """
        Train the net
        """
        # for epoch in self.config.epochs:
        data, labels = self.dataset.get_batch()
        labels = tf.one_hot(labels, self.dataset.n_labels)
        feed_dict = {self.input_ph: data,
                     self.label_ph: labels}
        loss, _ = self.session.run([self.loss, self.train_op], feed_dict=feed_dict)
        print('Epoch: {}/{}, loss: {}...'.format(epoch+1, self.config.epochs, loss))

    def validate(self):
        """
        Validate the current model on the test set
        """
        data, labels = self.dataset.test_set, self.dataset.test_labels
        output = self.classify(data)
        output_labels = np.argmax(output, axis=1)
        misclassified = output == output_labels
        n_misclassified = np.sum(misclassified)
        print('Test set: misclassified {}/{}'.format(n_misclassified, len(labels)))

    def classify(self, x):
        """
        Forward pass through the net
        """
        with self.session as sess:
            feed_dict = {self.input_ph: x} #, self.output_ph: np.random.randint(0, 4, [1,4])
            out = sess.run(self.output, feed_dict=feed_dict)
            return np.squeeze(out)

    def save(self):
        pass

    def load(self):
        pass

    


