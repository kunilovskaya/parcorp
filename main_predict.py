# coding: utf-8
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
from keras import backend
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
lang = 'en'
repository = lang + '_h5_main/'

fh_m = [f for f in os.listdir(repository)]
for f in fh_m:
    if f.endswith('.h5'):
        model_file = f
    elif f.endswith('.map'):
        w2i = pickle.load(open(repository + f, 'rb'))

maxlen = 1000
batch_size = 64
topk = 10

# Настраиваем логирование:
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)

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

rootdir = "/home/masha/gpuTF/metry/new_anns/part1-6_70/"
# rootdir = '/home/masha/test/'
folder = rootdir.split('/')[-2]
print(folder)
counter = 0
fns = []
# preds_nested = []
res_to = lang + '_nn_res_main/'
os.makedirs(res_to, exist_ok=True)
with open(res_to + '%s_%s_main.pred' % (lang, folder), "w") as outf:
    preds_nested = []
    for subdir, dirs, files in os.walk(rootdir):
        for i, file in enumerate(files):
            filepath = subdir + os.sep + file
            my_cat = (subdir + os.sep).split('/')[-3:-1]
            my_cat = '_'.join(my_cat)
            counter += 1
            fns.append(file)
            text = open(filepath, 'r').read()
            # t = Tokenizer(10000, lower=True)
            input = ['[#]' if w.isdigit() or any(char.isdigit() for char in w) else w for w in
                     text_to_word_sequence(text)]
            
            predicted = textf_predict(input, w2i, i)
            for preds in predicted:
                outstr = ['__label__%s %.3f' % (ann_order[i], preds[i]) for i in np.argsort(-preds)[:topk]]
                print('\t'.join(outstr), file=outf)
                ### lets produce a ML comparable output
                preds_nested.append(predicted[0].tolist())
        if counter % 100 == 0:
            print('I have predicted functional vectors for %s texts' % counter)
            # print('\t'.join(outstr), file=sys.stderr)
        print('%s predictions (in the unstacked weird format kept for historic reasons, see above) are written to %s_%s_main.pred' % (counter, lang, folder), file=sys.stderr)

    print(preds_nested)
    # set defaulf format to float This is NOT rounding!!!
    # pd.options.display.float_format = '{:.3f}'.format
    
    ## and also produce res for the above preds!!!
    df = pd.DataFrame(preds_nested).round(6)
    df.columns = [mapping[ann_order[x]] + ann_order[x] for x in range(len(ann_order))]
    df.insert(0, 'ID', fns)
    print(df.head(), file=sys.stderr)

    df.to_csv(res_to + '%s_%s_predicted_main.res' % (lang,folder), index=False, sep='\t')  # make sure to rename the file and move it tot the analysis script folder!!

    print('%s predictions are written to a table %s_predicted_main.res' % (counter, folder), file=sys.stderr)
  