'''
updated March 25, 2020
based on https://github.com/akutuzov/webvectors/blob/master/preprocessing/rus_preprocessing_udpipe.py

pre-process prepared texts (not necessarily one-sent per line) to get three versions of the corpus
- one-sent-per-line punct-tokenized txt,
- a conllu-format corpus and
- a lempos-represented corpus

The script expects:
(1) a path to files to be preprocessed (assumingly a subcorpus name: e.g. en, ru)
(2) a path where to store the output; you don't have to create a folder, just say where to create it
(3) the UD models for en, ru in the working folder (from which this script is run)
(4) the preprocess_imports.py module with the functions to be imported

USAGE:
-- go to parsing folder
-- python3 raw2txt2conllu2lempos.py --raw cleandata/mock_data/ --outto parsed/ --lang en
'''

import argparse
import zipfile, io, sys
from preprocess_functions import * #tokeniseall, unify_sym, postprocess_ud, do_job
from smart_open import open

parser = argparse.ArgumentParser()
parser.add_argument('--raw', help="Path to a folder (or a tree of folders) of raw txt files", required=True)
# processed makes sense as a dirname
parser.add_argument('--outto', help="Path to the root folder to hold input/txt, conllu and lempos subs", required=True)
parser.add_argument('--lang', type=str, required=True, help='Choose language: en, ru')

args = parser.parse_args()

# rootpath = args.raw ##/home/masha/HTQE/data/good-bad_processed/good/

start = time.time()

# # functional = set('ADP AUX CCONJ DET PART PRON SCONJ PUNCT'.split())
lang = args.lang

if lang == 'ru':
    # # STOPWORDS_FILE = 'stopwords_ru'
    # # stopwords = set([w.strip().lower() for w in smart_open(STOPWORDS_FILE,'r').readlines()])
    udpipe_filename = 'udpipe_syntagrus.model'
    model = Model.load(udpipe_filename)
    pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
if lang == 'en':
    # # STOPWORDS_FILE = 'stopwords_ru'
    # # stopwords = set([w.strip().lower() for w in smart_open(STOPWORDS_FILE,'r').readlines()])
    udpipe_filename = 'english-ewt-ud-2.3-181115.udpipe'
    model = Model.load(udpipe_filename)
    pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')

# use an external counter when tagging separate files, not onebig
counter = 0

rootout = args.outto
os.makedirs(rootout, exist_ok=True)

subcorp = args.raw.split('/')[-2]
out = rootout + subcorp + '/'
os.makedirs(out, exist_ok=True)

txt_out = out + 'sent_tok/'
os.makedirs(txt_out, exist_ok=True)

conllu_out = out + '/conllu/'
os.makedirs(conllu_out, exist_ok=True)

lempos_out = out + '/lempos/'
os.makedirs(lempos_out, exist_ok=True)

if args.raw.endswith('.zip'):
    z = zipfile.ZipFile(args.raw)
    
    for id,f in enumerate(z.namelist()):
        f0 = f.split('/')[1]
        counter += 1
        if id >= 1: ## we need to skip the first line which is the name of the containing folder
            txt_outf = txt_out + f0
            # print(txt_out, f0)
            ud_outf = conllu_out + f0.replace('.txt', '.conllu')
            temp_outf = out + f0.replace('.txt', '.temp')
            lempos_outf = lempos_out + f0.replace('.txt', '.lempos')
            
            with z.open(f) as readfile:
                with io.TextIOWrapper(readfile, encoding='utf-8') as input_text:
                    try:
                        text = input_text.read().strip()
                    except UnicodeDecodeError:
                        print(f)
                        continue
            
                    do_job(pipeline, text, txt_outf, ud_outf, temp_outf, lempos_outf, txt_sents=True, lang=lang)
        ### Monitor processing:
        if id % 50 == 0:
            print('%s files processed' % id, file=sys.stderr)
    z.close()
### if there is a tree of folders to walk below the rootdir
if args.raw.endswith('/'):
    print(args.raw)
    for subdir, dirs, files in os.walk(args.raw):
        for id, f in enumerate(files):
            counter += 1
            filepath = subdir + os.sep + f
            with open(filepath, 'r', errors='ignore') as input_text:
                txt_outf = txt_out + f
                ud_outf = conllu_out + f.replace('.txt', '.conllu')
                temp_outf = out + f.replace('.txt', '.temp')
                lempos_outf = lempos_out + f.replace('.txt', '.lempos')
                
                try:
                    text = input_text.read().strip()
                except UnicodeDecodeError:
                    print(f)
                    continue
                
                do_job(pipeline, text, txt_outf, ud_outf, temp_outf, lempos_outf, txt_sents=True, lang=lang)
    
        ### Monitor processing:
        if counter % 50 == 0:
            print('%s files processed' % counter, file=sys.stderr)
end = time.time()

processing_time = int(end - start)
print('Processing %s (%s files) took %.2f minites' % (args.raw, counter, processing_time / 60), file=sys.stderr)
