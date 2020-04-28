'''
updated March 28, 2020

run UDpipe on prepared texts stored in tgz compressed archives to get:
- temporary folders of *.conllu and UD-taggged texts (*.lempos)
- 2 tgz archives with each output in tgz_store location; names are inhereted from input archives

The script expects:
(1) a path to a folder with *.tgz files
(2) a path where to store the parsed texts and compressed archives; you don't have to create a folder, just say where to create it
(3) the UD models for en, ru in the working folder (from which this script is run)
(4) the cleaners_parsers.py module with the functions to be imported

USAGE:
-- go to parsing folder
-- python3 tgz2conllu2lempos.py --raw ~/temp/ --outto ~/enparsed/ --tgz_store ~/my_tgz/ --lang en
Used:

'''

import tarfile
import os, sys
from ufal.udpipe import Model, Pipeline
from cleaners_parsers import do_conllu2lempos, postprocess_ud
import time
import glob

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--raw', help="Path to the folder with *.tgz holding raw txt files", required=True)
parser.add_argument('--outto', help="Path to the root folder to hold conllu and lempos subdirectories", required=True)
parser.add_argument('--tgz_store', help="Path to the tgz storage", required=True)
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
store = args.tgz_store + '%s/' % lang
os.makedirs(store, exist_ok=True)

fh = [f for f in os.listdir(args.raw) if f.endswith('.tgz')]
for tarball in fh:
    regfolder = tarball.rstrip('.tgz')  # register
    print(regfolder)
    
    conllu_out = out + 'conllu/' + regfolder + '/'
    os.makedirs(conllu_out, exist_ok=True)
    
    lempos_out = out + 'lempos/' + regfolder + '/'
    os.makedirs(lempos_out, exist_ok=True)
    
    with tarfile.open(args.raw + tarball, "r:gz") as tar:
    
        for name, member in zip(tar.getnames(),tar.getmembers()):
             f = tar.extractfile(member)
             if f is not None:
                counter += 1
                fn = name.split('/')[-1]  # ./filename.txt
                print(fn)
                # folder = name.split('/')[0] + '/'  # I used to have media/filename.txt
                ud_outf = conllu_out + fn.replace('.txt', '.conllu')
                lempos_outf = lempos_out + fn.replace('.txt', '.lempos')
                
                try:
                    text = f.read().strip().decode('utf-8')
                except UnicodeDecodeError:
                    continue
                    
                parsed = do_conllu2lempos(pipeline, text, ud_outf)
                
                postprocess_ud(parsed, lempos_outf, entities=None, lang=lang)
                
    # tarballing the new folders
    with tarfile.open(store + regfolder + '_conllu.tgz', 'w:gz') as contgz, tarfile.open(store + regfolder + '_lempos.tgz', 'w:gz') as lemtgz:
        for file in glob.glob(os.path.join(conllu_out, "*.conllu")):
            contgz.add(file, os.path.basename(file))
        for file in glob.glob(os.path.join(lempos_out, "*.lempos")):
            lemtgz.add(file, os.path.basename(file))
    
    # Monitor processing:
    if counter % 100 == 0:
        print('%s files processed' % counter, file=sys.stderr)
    end = time.time()
    
    processing_time = int(end - start)
    print('Processing %s (%s files) took %.2f minites' % (args.raw, counter, processing_time / 60), file=sys.stderr)
