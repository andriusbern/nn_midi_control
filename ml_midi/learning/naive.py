import numpy as np

class RetardedClassifier(object):
    def __init__(self):
        self.n_classes = 5

    def classify(self, input):
        return np.random.randint(0,self.n_classes)