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
(3) a path where to store the output; you don't have to create it, just say where to create it
(4) the UD models for your languages in the working folder (from which this script is run)
(5) UDpipe installed: pip install ufal.udpipe
(6) the cleaners_parsers.py module with the functions to be imported
(7) use conllu_only=True: it is a switch to reduce the output to *.conllu only

USAGE:
-- go to parsing folder
-- run: python3 multiling2conllu2lempos.py --texts ../cleandata/mock_data/ --outto ../mock_parse/ --langs en ru
'''
import os, sys
from ufal.udpipe import Model, Pipeline
import time
import argparse
from cleaners_parsers import do_conllu_only, do_job
from smart_open import open

parser = argparse.ArgumentParser()
parser.add_argument('--rootdir', help="Path to a folder (or a tree of folders) of prepared txt files", required=True)
parser.add_argument('--conllu_out', help="Path to the root folder to hold the resulting parsed data", required=True)
parser.add_argument('--lempos_out', help="Path to the root folder to hold the resulting UD-tagged texts", required=True)
parser.add_argument('--langs', nargs='+', default=['en','ru'], help='Pass language indices like so: --langs en ru')
args = parser.parse_args()

start = time.time()

parse_out = args.conllu_out
os.makedirs(parse_out, exist_ok=True)
languages = args.langs

# do you really want lempos too?
conllu_only = True

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
        print('Did yoy forget to indicate the language with the script argument --lang, ex. --lang en ?')

print('UD models loaded')
print('If you get no output and no errors, check the path to the cleandata')

counter = 0
for subdir, dirs, files in os.walk(args.texts):
    for id, f in enumerate(files):
        last_folder = subdir + os.sep
        lang_folder = len(os.path.abspath(last_folder).split('/')) - 1
        lang = os.path.abspath(last_folder).split('/')[lang_folder]
    
        if conllu_only:
            out = parse_out + '/'.join(last_folder.split('/')[-4:-1]) + '/'
            os.makedirs(out, exist_ok=True)
            counter += 1
            filepath = subdir + os.sep + f
            with open(filepath, 'r', errors='ignore') as input_text:
                ud_outf = out + f.replace('.txt', '.conllu')
    
                try:
                    text = input_text.read().strip()
                except UnicodeDecodeError:
                    print('Failed to read:', f)
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
