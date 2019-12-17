import tensorflow as tf
import numpy as np
from ml_midi.config import ConfigManager as conf
from random import shuffle
# from data_handler import DataIO, Dataset
from ml_midi.processing import DataIO, Dataset
import time, os, datetime

mlp_config = dict(
    dataset='test_guitar_2k',
    fc_layers=[512, 256, 128, 32],
    batch_size=1000,
    epochs=250,
    lr=0.001
    )


class MLP(object):
    """
    Save net parameters in YAML files
    """
    def __init__(self, config, dataset):
        date = datetime.datetime.now().strftime("%m-%d_%H:%M:%S")
        self.name = 'MLP__d({})_fc{}_b{}_{}'.format(
            dataset.name, config['fc_layers'], config['batch_size'], date)

        self.counter = 0
        self.dataset = dataset
        self.dims = dataset.samples.shape[1:]
        self.n_categories = len(np.unique(dataset.data_labels))
        self.dir = os.path.join(conf.SRC_DIR, 'logs', self.name)
        os.mkdir(self.dir)

        self.lr = config['lr']
        self.config = config
        self.graph = tf.Graph()
        self.setup()

        self.session = tf.Session(graph=self.graph)
        self.writer = tf.summary.FileWriter(self.dir, self.session.graph)
        self.session.run(self.init)
        # self.saver = tf.train.Saver()
        self.model_path = os.path.join(conf.SRC_DIR, 'models', self.name + '.cpkt')

    def setup(self):
        with self.graph.as_default():
            self._placeholders()
            self._build_net()
            self.summary_init()
            self.loss = tf.reduce_mean(tf.square(self.output - self.label_ph), name='loss')
            self.train_op = tf.train.AdamOptimizer(self.lr).minimize(self.loss)
            self.init = tf.global_variables_initializer()

    def load(path):
        self.output = tf.get_variable()
        # for var in self.graph.get_collection('trainable_variables'):



    def summary_init(self):
        with tf.name_scope('performance'):
            self.loss_ph = tf.placeholder(tf.float32,shape=None,name='loss_summary') 

            self.te_acc_ph = tf.placeholder(tf.float32,shape=None, name='train_acc') 
            self.tr_acc_ph = tf.placeholder(tf.float32,shape=None, name='test_acc')

            self.loss_summary = tf.summary.scalar('loss', self.loss_ph)
            self.tr_acc_summary = tf.summary.scalar('train_accuracy', self.tr_acc_ph)
            self.te_acc_summary = tf.summary.scalar('test_accuracy', self.te_acc_ph)

        self.all_summaries = tf.summary.merge([self.loss_summary, self.tr_acc_summary, self.te_acc_summary])

    def _placeholders(self):
        self.input_ph = tf.placeholder(tf.float32, shape=(None, self.dims[0] * self.dims[1]), name='input')
        self.label_ph = tf.placeholder(tf.float32, shape=(None, self.n_categories), name='labels')
        
    def _build_net(self):
        """
        Build the network based on the network config parameters
        """

        output = tf.layers.dense(
            self.input_ph,
            self.config['fc_layers'][0],
            activation=tf.nn.relu,
            name='fc0')

        # Fully connected layers
        output = tf.layers.flatten(output)
        for i, layer in enumerate(self.config['fc_layers'][1:]):
            output = tf.layers.dense(
                output,
                layer,
                activation=tf.nn.relu,
                name='fc{}'.format(i+1))

        output = tf.layers.dense(
            output,
            self.n_categories,
            activation=tf.nn.softmax,
            name='output')

        self.output = output


    def set_dataset(self, dataset):
        self.dataset = dataset

    def train(self, size=10):
        """
        Train the net
        """
        data, labels = self.dataset.get_batch(size)
        data = data.reshape([data.shape[0], data.shape[1]*data.shape[2]])
        feed_dict = {self.input_ph: data,
                     self.label_ph: labels}
        t0 = time.time()

        out, loss, _ = self.session.run([self.output, self.loss, self.train_op], feed_dict=feed_dict)

        output_labels = np.argmax(np.squeeze(out), axis=1)
        print('TRAIN: =====================')
        print('out: ', output_labels)
        print('tar: ', np.argmax(labels, axis=1))
        acc = np.sum(output_labels == np.argmax(labels, axis=1)) / len(labels) # Train accuracy
        te_acc, _ = self.validate() # Test acc
        
        # Summary
        summary = self.session.run(self.all_summaries, {self.loss_ph: loss, self.te_acc_ph: te_acc, self.tr_acc_ph: acc})

        print(time.time() - t0)
        self.writer.add_summary(summary, self.counter)
        self.counter += 1
        return loss, acc, te_acc

    def validate(self):
        """
        Validate the current model on the test set
        """
        data, labels = self.dataset.test_x, self.dataset.test_y
        data = data.reshape([data.shape[0], data.shape[1]*data.shape[2]])
        nl = len(self.dataset.labels)
        confmat = np.zeros([nl, nl])
        output = self.classify(data)
        output_labels = np.argmax(output, axis=1)
        misclassified = output_labels == labels
        n_misclassified = np.sum(misclassified)
        print('Test set: correct classifications {}/{}'.format(n_misclassified, len(labels)))
        percent = n_misclassified/len(labels)
        for l, o in zip(labels, output_labels):
            confmat[l,o] += 0 if l==o else 1

        return percent, confmat

    def classify(self, x):
        """
        Forward pass through the net
        """
        print(x.shape)
        try:
            feed_dict = {self.input_ph: x} 
            out = self.session.run(self.output, feed_dict=feed_dict)
        except:
            data = x.reshape([x.shape[0], x.shape[1]*x.shape[2]])
            print(data.shape)
            feed_dict = {self.input_ph: data} 
            out = self.session.run(self.output, feed_dict=feed_dict)
        return np.squeeze(out)

    def test(self, s, e):
        
        data = self.dataset.samples[s:e, :, :]
        data = np.expand_dims(data, axis=3)
        feed_dict = {self.input_ph: data}
        out = self.session.run(self.output, feed_dict=feed_dict)
        categories = np.argmax(out, axis=1)

        return np.squeeze(out), categories

    def save(self):
        self.saver.save(sess, self.model_path)

    # def load(self):
        

    


