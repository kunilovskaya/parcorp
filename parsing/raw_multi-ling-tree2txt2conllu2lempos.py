# coding: utf-8
'''
pre-process multiling tree of folders with raw texts (not necessarily one-sent per line)
into one-sent-per-line punct-tokenized txt, conllu corpus and a lempos corpus

use available filters to adjust the required format for each of the three outputs
the script expects:
(1) a path to the root of the tree (last folder has lang index as the name) to be preprocessed
(2) a path where to store the output; you don't have to create it, just say where to create it
(3) the UD models for en, ru in the working folder (from which this script is run)
(4) the preprocess_imports.py module with the functions to be imported
(5) use conllu_only = True: switch to reduce the output to conllu only

USAGE:
-- go to parsing folder
-- run: python3 raw_multi-ling-tree2txt2conllu2lempos.py --texts ../rawdata/mock_data/ --outto ../mock_parse/
'''
import os, sys
from ufal.udpipe import Model, Pipeline
import time
import argparse
from preprocess_functions import do_conllu_only, do_job
from smart_open import open

parser = argparse.ArgumentParser()
parser.add_argument('--texts', help="Path to a folder (or a tree of folders) of prepared txt files", required=True)
# processed makes sense as a dirname
parser.add_argument('--outto', help="Path to the root folder to hold the resulting tree ending with sent_tok/, conllu/ and lempos/ subs", required=True)


args = parser.parse_args()

start = time.time()

rootout = args.outto
os.makedirs(rootout, exist_ok=True)

# do you really want all three formats of your corpus? I don't think so
conllu_only = True

# specify models for your languages (and stoplists, if required)
# to use these lists, activate keyworded parameters in check_word function in preprocess_function module
# STOPWORDS_FILE1 = '/path/to/ru_stopwords.txt'
# stopwords = set([w.strip().lower() for w in smart_open(STOPWORDS_FILE1,'r').readlines()])
# STOPWORDS_FILE2 = '/path/to/en_stopwords.txt'
# stopwords = set([w.strip().lower() for w in smart_open(STOPWORDS_FILE2,'r').readlines()])
# functional = set('ADP AUX CCONJ DET PART PRON SCONJ PUNCT'.split())

ru_udpipe_filename = 'udpipe_syntagrus.model'
ru_model = Model.load(ru_udpipe_filename)
ru_pipeline = Pipeline(ru_model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')

en_udpipe_filename = 'english-ewt-ud-2.3-181115.udpipe'
en_model = Model.load(en_udpipe_filename)
en_pipeline = Pipeline(en_model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')

print('UD models loaded')
print('If you get no output and no errors, check the path to the rawdata')

counter = 0
for subdir, dirs, files in os.walk(args.texts):
    for id, f in enumerate(files):
        last_folder = subdir + os.sep
        lang_folder = len(os.path.abspath(last_folder).split('/')) - 1
        lang = os.path.abspath(last_folder).split('/')[lang_folder]
    
        if conllu_only:
            out = rootout + '/'.join(last_folder.split('/')[-4:-1]) + '/'
            os.makedirs(out, exist_ok=True)
            counter += 1
            filepath = subdir + os.sep + f
            with open(filepath, 'r', errors='ignore') as input_text:
                ud_outf = out + f.replace('.txt', '.conllu')
    
                try:
                    text = input_text.read().strip()
                except UnicodeDecodeError:
                    print(f)
                    continue
                if lang == 'en':
                    do_conllu_only(en_pipeline, text, lang, ud_outf)
                elif lang == 'ru':
                    do_conllu_only(ru_pipeline, text, lang, ud_outf)
    
                ### Monitor processing:
                if counter % 50 == 0:
                    print('%s files processed' % counter, file=sys.stderr)
        else:
            out = rootout + '/'.join(last_folder.split('/')[-4:-1])
            os.makedirs(out, exist_ok=True)
            
            txt_out = out + '/sent_tok/'
            os.makedirs(txt_out, exist_ok=True)
            
            conllu_out = out + '/conllu/'
            os.makedirs(conllu_out, exist_ok=True)
            
            lempos_out = out + '/lempos/'
            os.makedirs(lempos_out, exist_ok=True)

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
                # select txt_sents=False if you don't want one-sentence-per-line format!
                if lang == 'en':
                    do_job(en_pipeline, text, txt_outf, ud_outf, temp_outf, lempos_outf, txt_sents=True, lang=lang)
                elif lang == 'ru':
                    do_job(ru_pipeline, text, txt_outf, ud_outf, temp_outf, lempos_outf, txt_sents=True, lang=lang)
                    
                ### Monitor processing:
                if counter % 50 == 0:
                    print('%s files processed' % counter, file=sys.stderr)

end = time.time()
processing_time = int(end - start)
print('Processing %s (%s files) took %.2f minites' % (args.texts, counter, processing_time / 60), file=sys.stderr)
