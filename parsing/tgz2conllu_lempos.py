'''
updated March 25, 2020
based on https://github.com/akutuzov/webvectors/blob/master/preprocessing/rus_preprocessing_udpipe.py

pre-process prepared texts (not necessarily one-sent per line) to get three versions of the corpus
- one-sent-per-line punct-tokenized txt,
- a conllu-format corpus and
- a lempos-represented corpus

The script expects:
(1) a path to a folder with files to be preprocessed
(2) a path where to store the output; you don't have to create a folder, just say where to create it
(3) the UD models for en, ru in the working folder (from which this script is run)
(4) the cleaners_parsers.py module with the functions to be imported

USAGE:
-- go to parsing folder
-- python3 simple_raw2conllu2lempos.py --raw cleandata/mock_data/fiction/source/en/ --outto parsed/ --lang en
'''

import argparse
import tarfile
import os, sys
from ufal.udpipe import Model, Pipeline
from cleaners_parsers import do_conllu_lempos
import time


parser = argparse.ArgumentParser()
parser.add_argument('--raw', help="Path to a folder (or a tree of folders) of raw txt files", required=True)
parser.add_argument('--outto', help="Path to the root folder to hold txt, conllu and lempos subdirectories", required=True)
parser.add_argument('--lang', type=str, required=True, help='Choose language: en, ru')

args = parser.parse_args()

start = time.time()

## functional = set('ADP AUX CCONJ DET PART PRON SCONJ PUNCT'.split())
lang = args.lang

if lang == 'ru':
    udpipe_filename = 'udpipe_syntagrus.model'
    model = Model.load(udpipe_filename)
    pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
elif lang == 'en':

    udpipe_filename = 'english-ewt-ud-2.3-181115.udpipe'
    model = Model.load(udpipe_filename)
    pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
else:
    pipeline = None
    print('Did yoy forget to indicate the language with the script argument --lang, ex. --lang en ?')


counter = 0

out = args.outto
os.makedirs(out, exist_ok=True)

fh = [f for f in os.listdir(args.raw)]
for tarball in fh:
    folder = tarball.rstrip('.tgz')
    print(folder)
    
    conllu_out = out + folder + '/conllu/'
    os.makedirs(conllu_out, exist_ok=True)
    
    lempos_out = out + folder + '/lempos/'
    os.makedirs(lempos_out, exist_ok=True)
    
    tar = tarfile.open(args.raw + tarball, "r:gz")
    
    for name, member in zip(tar.getnames(),tar.getmembers()):
         f = tar.extractfile(member)
         if f is not None:
            counter += 1
            fn = name.split('/')[-1]
            folder = name.split('/')[0] + '/'
            ud_outf = conllu_out + folder + fn.replace('.txt', '.conllu')
            lempos_outf = lempos_out + folder + fn.replace('.txt', '.lempos')
            
            try:
                text = f.read().strip().decode('utf-8')
            except UnicodeDecodeError:
                continue
                
            do_conllu_lempos(pipeline, text, ud_outf, lempos_outf, lang=lang)
    
    ### Monitor processing:
    if counter % 50 == 0:
        print('%s files processed' % counter, file=sys.stderr)
    end = time.time()
    
    processing_time = int(end - start)
    print('Processing %s (%s files) took %.2f minites' % (args.raw, counter, processing_time / 60), file=sys.stderr)
