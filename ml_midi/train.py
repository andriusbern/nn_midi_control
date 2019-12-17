from ml_midi.processing import ImageDataset, Dataset
from ml_midi.learning import ConvNet, MLP
import ml_midi

conf = ml_midi.config.net_config

audio = Dataset(conf['dataset'], True)
audio.write_image_dataset(.6)

data = ImageDataset(conf['dataset'])
data.show(50)


net = MLP(conf, data)

try:
    for i in range(conf['epochs']):
        print('Epoch {}...'.format(i+1))
        net.train(conf['batch_size'])
except KeyboardInterrupt:
    print('Stop.')    

_, confmat = net.validate()

print(data.labels)
print(confmat)
input()

