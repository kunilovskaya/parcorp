# coding: utf-8
# get predictions for 10 functional text categories from a model pre-trained on CC-vector representations of raw text tokens
## specify language
## assumes that input is a folder of raw texts to predict

import time

starttime = int(time.time())
import logging

import sys, os
import pickle
import pandas as pd

import numpy as np
import smallutils as ut
from keras.models import load_model as load_keras_model

from keras.preprocessing import sequence
import tensorflow as tf
from keras import backend as K
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from nn_train_cv import AttentionWeightedAverage

## infile should be a list of text wds
def textf_predict(infile, dic, i=0):
    x_test = []  # indices collector
    if i == 0:
        print("Number of words in text 0", len(infile), file=sys.stderr)
        print('First five:', infile[:5], file=sys.stderr)
    for w in infile:
        if not w in dic.keys():
            w = '<unk>'
        x_test.append(dic[w])
    if i == 0:
        print('Beginning of the same text 0 represented as indices', x_test[:10], file=sys.stderr)
    
    x = sequence.pad_sequences([x_test], maxlen=maxlen)
    # print(x)
    if i == 0:
        print("Number of indices in text 0 (a [list] now!) after padding should be 1000", len(x[0]), file=sys.stderr)
        
    predict = model.predict(x, batch_size=batch_size)
    # predict = [i[0] for i in predict]
    if i == 0:
        print("What is actually returned for text 0", predict, file=sys.stderr)
    predict = np.vstack(predict)
    predict = np.transpose(predict)
    if i == 0:
        print('====',predict)
    return predict ## list of arrays

##############################
## load model to use for prediction
##############################
device = 'gpu' # cpu

if device == 'cpu':
    ## select the number of CPU workers=threads to be used
    config = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=4,
                                      inter_op_parallelism_threads=4,
                                      allow_soft_placement=True)  # ,device_count = {'CPU' : 2, 'GPU' : 1}
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
if device == 'gpu':
    config = tf.compat.v1.ConfigProto()
    # os.environ["CUDA_VISIBLE_DEVICES"]="0,1"
    print('=== DEFAULT availability', K.tensorflow_backend._get_available_gpus())
    # sess = tf.Session(config=config)
    ## select what you want to run it on
    # config = tf.ConfigProto(device_count={'GPU': 0, 'CPU': 4})
    # config.gpu_options.visible_device_list = '1'  # only see the gpu 1
    config.gpu_options.visible_device_list = '0,1'  # see the gpu 0, 1, 2
    
    ## replace: tf.ConfigProto by tf.compat.v1.ConfigProto
    print("====== Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
    
    tf.compat.v1.logging.set_verbosity(tf.logging.INFO)


lang = 'en'
repository = 'models/'

fh_m = [f for f in os.listdir(repository)]
for f in fh_m:
    if f.endswith('.h5'):
        model_file = f
    elif f.endswith('.map'):
        w2i = pickle.load(open(repository + f, 'rb'))

maxlen = 1000
batch_size = 64
topk = 10

# logger.info('Load a pre-trained Keras model...')
model = load_keras_model(repository + model_file, custom_objects={"AttentionWeightedAverage": AttentionWeightedAverage})
# print(model.summary())

print('Predicting on:', file=sys.stderr)

mapping = {'A1': 'argument', 'A16': 'info', 'A8': 'news', 'A11': 'personal', 'A17': 'eval', 'A12': 'promotion',
           'A14': 'scitech', 'A9': 'legal', 'A7': 'instruction', 'A4': 'fiction'}

# this is the exact order of the y in the model training setting
ann_order = ['A1', 'A4', 'A7', 'A8', 'A9', 'A11', 'A12', 'A14', 'A16', 'A17']
print('what are we predicting', ann_order, file=sys.stderr)

###########################
### input folder (two-level tree of folders) or file
###########################

rootdir = "data/yandex/"
folder = rootdir.split('/')[-2]
print(folder)
counter = 0
fns = []
# preds_nested = []

preds_nested = []
files = [f for f in os.listdir(rootdir) if f.endswith('.txt')]
for i, file in enumerate(files):
    counter += 1
    fns.append(file)
    text = open(rootdir + file, 'r').read()
    input = ['[#]' if w.isdigit() or any(char.isdigit() for char in w) else w for w in
             text_to_word_sequence(text)]
    
    predicted = textf_predict(input, w2i, i)
    preds_nested.append(predicted[0].tolist())
if counter % 100 == 0:
    print('I have predicted functional vectors for %s texts' % counter)
    # print('\t'.join(outstr), file=sys.stderr)

print(preds_nested)
# set defaulf format to float This is NOT rounding!!!
# pd.options.display.float_format = '{:.3f}'.format

## and also produce res for the above preds!!!
df = pd.DataFrame(preds_nested).round(6)
df.columns = [mapping[ann_order[x]] + ann_order[x] for x in range(len(ann_order))]
df.insert(0, 'ID', fns)
print(df.head(), file=sys.stderr)

df.to_csv(repository + '%s_%s_predicted_main.res' % (lang,folder), index=False, sep='\t')

print('%s predictions are written to a table %s_predicted_main.res' % (counter, folder), file=sys.stderr)
  