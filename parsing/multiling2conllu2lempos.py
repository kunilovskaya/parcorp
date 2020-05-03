'''
updated April 26, 2020
This parsing setup assumes that you have a structure of folders representing your text categories for a language pair.
The folderes have preprocessed (clean) files, i.e. for example sententence lengths normalisation and symbol unification has been performed if necessary
The last folder name in the folder structure is the language index.

As the result of parsing you need the same folder structure containing
-- UD-parsed texts (*.conllu)
-- lemmatised and tagged files (*.lempos)
No filtering is done, i.e. you get the output WITH punctuation, function words, numerals as they appear in the input

The script expects:
(1) a path to the root of the tree (last folder has the lang index as its name) to be preprocessed
(2) the last folders in the structure should indicate the language (en, ru); these indices need to be passed to the --langs option
(3) adjust the names of the UD models in lines 56-60 for your languages; put the modela into the working dir (from which this script is run)
(5) UDpipe installed: pip install ufal.udpipe
(6) the cleaners_parsers.py module with the functions to be imported
(7) use --lempos switch if you also want the lemmatised and tagged (*.lempos) format of your corpus

The output folders are created in the working directory.

USAGE:
-- go to parsing folder
-- run: python3 multiling2conllu2lempos.py --rootdir clean/ --depth 3 --langs en ru --lempos
'''


import os, sys
from ufal.udpipe import Model, Pipeline
import time
import argparse
from cleaners_parsers import do_conllu_only, do_conllu2lempos, postprocess_ud
from smart_open import open


parser = argparse.ArgumentParser()
parser.add_argument('--rootdir', help="Path to a folder (or a tree of folders) of prepared txt files", required=True)
parser.add_argument('--lempos', action="store_true", help="Use this flag if you want UD-tagged output saved to lempos/ folder")
parser.add_argument('--langs', nargs='+', default=['en','ru'], help='Pass language indices like so: --langs en ru')
parser.add_argument('--depth', default=3, type=int, help='Depth of the folder structure under rootdir. Example: for clean/ted/ref/ru/ depth=3')
args = parser.parse_args()

start = time.time()

languages = args.langs

parse_out = 'conllu/'
os.makedirs(parse_out, exist_ok=True)
if args.lempos:
    lemp_out = 'lempos/'
    os.makedirs(lemp_out, exist_ok=True)
else:
    lemp_out = None

for language in languages:
    if language == 'ru':
        ru_udpipe_filename = 'udpipe_syntagrus.model'
        ru_model = Model.load(ru_udpipe_filename)
        ru_pipeline = Pipeline(ru_model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
    elif language == 'en':
        en_udpipe_filename = 'english-ewt-ud-2.3-181115.udpipe'
        en_model = Model.load(en_udpipe_filename)
        en_pipeline = Pipeline(en_model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
    else:
        pipeline = None
        print('Did you forget to indicate the language with the script argument --lang, ex. --lang en ?')

print('UD models loaded')
print('If you get no output and no errors, check the path to the input')


counter = 0
for subdir, dirs, files in os.walk(args.rootdir):
    for id, f in enumerate(files):
        last_folder = subdir
        lang_folder = len(os.path.abspath(last_folder).split('/')) - 1
        lang = os.path.abspath(last_folder).split('/')[lang_folder]
        
        udout = parse_out + '/'.join(last_folder.split('/')[-args.depth:]) + '/'
        os.makedirs(udout, exist_ok=True)
        ud_outf = udout + f.replace('.txt', '.conllu')
        
        if args.lempos:
            lempos = lemp_out + '/'.join(last_folder.split('/')[-args.depth:]) + '/'
            os.makedirs(lempos, exist_ok=True)
            lempos_outf = lempos + f.replace('.txt', '.lempos')
        else:
            lempos=None
            lempos_outf=None
        
        counter += 1
        filepath = subdir + os.sep + f
        with open(filepath, 'r', errors='ignore') as input_text:
            try:
                text = input_text.read().strip()
            except UnicodeDecodeError:
                print('Unicode error in input file: %s; skipping it' % f)
                continue
                
            if args.lempos:
                if lang == 'en':
                    parsed = do_conllu2lempos(en_pipeline, text, ud_outf)
                    postprocess_ud(parsed, lempos_outf, sentencebreaks=True, entities=None, lang=lang)
                elif lang == 'ru':
                    parsed = do_conllu2lempos(ru_pipeline, text, ud_outf)
                    postprocess_ud(parsed, lempos_outf, sentencebreaks=True, entities=None, lang=lang)
            else:
                if lang == 'en':
                    do_conllu_only(en_pipeline, text, ud_outf)
                elif lang == 'ru':
                    do_conllu_only(ru_pipeline, text, ud_outf)
                    
            ### Monitor progress:
            if counter % 10 == 0:
                print('%s files processed' % counter, file=sys.stderr)



end = time.time()
processing_time = int(end - start)
print('Processing %s (%s files) took %.2f minites' % (args.rootdir, counter, processing_time / 60), file=sys.stderr)
