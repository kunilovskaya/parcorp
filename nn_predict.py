# coding: utf-8
## specify language and representation
## for each representation (mixed/lex) and each language (en/ru) specify the path to the model you want to use to predict functionality of your input files
# put the folder to predict next to this script and run it from PyCharm and give the name of the folder below
# it creates .lang+'_nn_res/' folder for the outputs (*.res and *.pred) next to this script
# requires the training script nn_train_cv.py  to get the description of the architecture


# all args and switches are hardcoded, runs in PyCharm

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

from nn_train_cv import AttentionWeightedAverage

lang = 'ru'
reps = 'mixed'  # 'mixed', 'lex'
size = '2725'
name = lang + size + '_' + reps
# where are the files you want you predictions for? Are you sure they are the right format?
## for bnc predict on 650 text regardless the genre and then use bnc6cats.fns for ganre membership information
path = 'cross_case-study/rnc_main3M'  # 'new_anns/part1-6_70' NB! No final slash and split[1]!!  'en_lex0.3test' # en_nf_rltc 'en_nf_croco' #None #'en_nf_rltc' ## NB! needs no slash and has to be in the script folder
try:
    folder = path.split('/')[1]
except IndexError:
    folder = path

repository = lang + '_h5/'

fh_mods = [f for f in os.listdir(repository) if f.endswith('.h5')]
fh_maps = [f for f in os.listdir(repository) if f.endswith('.map')]
# or do you want to get a functional vector for just one file?
test_file = None  # 'en_0.3test.ol' #None #'EN_1_57.conllu.lem.nf' #None # 'EN_1_3.conllu.lem.nf' # test_file = 'some_lemmatized text'

## chossing and loading the reqired model
for mod in fh_mods:
    if name in mod:
        model_file = repository + mod
for map in fh_maps:
    if name in map:
        w2i = pickle.load(open(repository + map, 'rb'))

print("Mapping of features:", len(w2i), type(w2i), file=sys.stderr)
if reps == 'mixed':
    dictionary = 'nn_train_input/' + lang + '.brieftag.num'
    frqlimit = 1500

maxlen = 1000
batch_size = 64
topk = 10

# Настраиваем логирование:
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('Load a pre-trained Keras model...')
model = load_keras_model(model_file, custom_objects={"AttentionWeightedAverage": AttentionWeightedAverage})
print(model.summary())

print('Predicting on:', file=sys.stderr)

mapping = {'A1': 'argument', 'A16': 'info', 'A8': 'news', 'A11': 'personal', 'A17': 'eval', 'A12': 'promotion',
           'A14': 'scitech', 'A9': 'legal', 'A7': 'instruction', 'A4': 'fiction'}

# this is the exact order of the y in the model training setting
ann_order = ['A1', 'A4', 'A7', 'A8', 'A9', 'A11', 'A12', 'A14', 'A16', 'A17']
print('what are we predicting', ann_order, file=sys.stderr)

# prepare for writing output

counter = 0


def textf_predict(openf, i=0, reps=reps):
    x_test = []  # indices collector
    if reps == 'lex':
        testfile = [w for w in openf.split()]
    if reps == 'mixed':
        testfile = openf
    if i == 0:
        print("Number of words in text 0", len(testfile), file=sys.stderr)
        print('First five:', testfile[:5], file=sys.stderr)
    for w in testfile:
        if not w in w2i.keys():
            w = '<unk>'
        x_test.append(w2i[w])
    if i == 0:
        print('Beginning of the same text 0 represented as indices', x_test[:10], file=sys.stderr)
    
    x = sequence.pad_sequences([x_test], maxlen=maxlen)
    # print(x)
    if i == 0:
        print("Number of indices in text 0 (a [list] now!) after padding should be 400", len(x[0]), file=sys.stderr)
    predict = model.predict(x, batch_size=batch_size)
    
    if i == 0:
        print("What is actually returned for text 0", predict, file=sys.stderr)
    return predict


if folder:
    
    res_to = lang + '_nn_res/'
    os.makedirs(res_to, exist_ok=True)
    
    outname = '_'.join([folder, reps])
    # outf = open(outname + '.pred', "w")
    # get rid of annoying occasional *.txt that screw up at production stage
    files = []
    if reps == 'lex':
        fh = [f[:-14] for f in os.listdir(path) if f.endswith('.nf')]
    if reps == 'mixed':
        fh = [f[:-4] for f in os.listdir(path) if f.endswith('.txt')]
    
    for doc in fh:
        if doc.strip().endswith('.txt'):
            # print(doc, file=sys.stderr)
            doc = doc[:-4]
            files.append(doc)
        else:
            doc = doc
            files.append(doc)
    
    if len(fh) == len(files):
        pass
    else:
        print('Something went wrong with the filenames editing', file=sys.stderr)
    
    preds_nested = []
    
    ## This is needed to get preds in the new annotations experiment!
    with open(res_to + '%s_%s%s_biLSTMa.pred' % (folder, reps, size), "w") as outf:
        for i, file in enumerate(fh):
            if reps == 'lex':
                f = open(path + '/' + file + '.conllu.lem.nf').read()
                input = f
            if reps == 'mixed':
                # there were problems with filenames encoding inherited from windows
                f = open(path + '/' + file + '.txt', encoding='utf-8', errors='replace').read()
                # print('======', file, file=sys.stderr)
                dictlist, frqlist = ut.readfrqdict(dictionary, frqlimit)
                input = ut.mixedstr(f, dictlist, frqlist)
            predicted = textf_predict(input, i)
            for preds in predicted:
                outstr = ['__label__%s %.3f' % (ann_order[i], preds[i]) for i in np.argsort(-preds)[:topk]]
                print('\t'.join(outstr), file=outf)
                counter += 1
                ### lets produce a ML comparable output
                preds_nested.append(predicted[0].tolist())
                if counter % 100 == 0:
                    print('I have predicted functional vectors for %s texts' % counter)
                    print('\t'.join(outstr),file=sys.stderr)
        print('%s predictions (in the unstacked weird format kept for historic reasons, see above) are written to %s_%s%s_biLSTMa.pred for ' % (counter, folder, reps, size), file=sys.stderr)
        
        print(len(preds_nested))
        # set defaulf format to float This is NOT rounding!!!
        # pd.options.display.float_format = '{:.3f}'.format
        
        ### and also produce res for the above preds!!!
        df = pd.DataFrame(preds_nested).round(6)
        df.columns = [mapping[ann_order[x]] + ann_order[x] for x in range(len(ann_order))]
        df.insert(0, 'filename', files)
        # df.filename.replace('.conllu.lem.nf', '', regex=False)
        # df.round(3)
        print(df.head(), file=sys.stderr)
        
        df.to_csv(res_to + 'predicted_%s%s_biLSTMa.res' % (outname, size), index=False, sep='\t')  # 10ep1624
        
        print('%s predictions are written to a table %spredicted_%s%s_biLSTMa.res (see above)' % (counter, res_to, outname, size),
              file=sys.stderr)
    # outf.close()

if test_file != None:
    # this is the doublechecking scenario
    
    if test_file.endswith('.ol'):
        outname = test_file
        outf = open('doublechecking_' + outname + '.pred', "w")
        f = open(test_file).readlines()
        for i, file in enumerate(f):
            if reps == 'lex':
                input = file
            if reps == 'mixed':
                dictlist, frqlist = ut.readfrqdict(dictionary, frqlimit)
                input = ut.mixedstr(file, dictlist, frqlist)
            
            predicted = textf_predict(input, i)
            for preds in predicted:
                # this is standard 0.3test output: We want to be sure that this file returneds the same predictions as the main traindev one, don't we?
                outstr = ['__label__%s %.3f' % (ann_order[i], preds[i]) for i in np.argsort(-preds)[:topk]]
                print('\t'.join(outstr), file=outf)
                counter += 1
        
        print('%s predictions are written to %s' % (counter, outname + '.pred'), file=sys.stderr)
        outf.close()
    else:
        f = open(test_file).read()
        if reps == 'lex':
            input = f
        if reps == 'mixed':
            dictlist, frqlist = ut.readfrqdict(dictionary, frqlimit)
            input = [ut.mixedstr(l, dictlist, frqlist) for l in f]  # list of lists
        predicted = textf_predict(input, i=0)
        print("Here are the predictions on %s:" % (test_file), file=sys.stderr)
        for preds in predicted:
            for i in np.argsort(-preds)[:topk]:
                print("\t%s: %.3f" % (mapping[ann_order[i]], preds[i]), file=sys.stderr)

backend.clear_session()
testtime = int(time.time())
print('Time: %d min' % ((testtime - starttime) / 60), file=sys.stderr)
