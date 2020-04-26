## print research corpus stats based on UD annotated data

import os, sys
from collections import defaultdict

rootdir = "extract_translationese_features/parsed_data/regbalanced/"


def wordcount(trees):
    words = 0
    for tree in trees:
        words += len(tree)

    return words


def get_trees(data):  # data is one object: a text or all of corpus as one file
    sentences0 = []
    badsents = 0
    only_punct = []
    current_sentence = []
    for line in data:
        if line.strip() == '':
            if current_sentence:
                sentences0.append(current_sentence)
            
            current_sentence = []
            only_punct = []
            
            continue
        if line.strip().startswith('#'):
            continue
        res = line.strip().split('\t')
        (identifier, token, lemma, upos, xpos, feats, head, rel, misc1, misc2) = res
        if '.' in identifier or '-' in identifier:  # ignore empty nodes possible in the enhanced representations
            continue
        
        for i in res:
            only_punct.append(res[3])
        var = list(set(only_punct))
        # throw away sentences consisting of punctuation marks only (ex. '.)') and of numeral and a punctuation (ex. '3.', 'II.')
        if len(var) == 1 and var[0] == 'PUNCT':
            continue
        if len(var) == 2 and 'PUNCT' in var and 'NUM' in var:
            badsents += 1
        else:
            current_sentence.append((int(identifier), token, lemma, upos, xpos, feats, int(head), rel))
    
    if current_sentence:
        sentences0.append(current_sentence)
    
    sentences = [s for s in sentences0 if len(s) >= 4]
    shorts = len(sentences0) - len(sentences)
    
    return sentences, badsents, shorts


def get_meta(input):
    # prepare for writing metadata
    lang_folder = len(os.path.abspath(input).split('/')) - 1
    status_folder = len(os.path.abspath(input).split('/')) - 2
    register_folder = len(os.path.abspath(input).split('/')) - 3
    
    status0 = os.path.abspath(input).split('/')[status_folder]
    register0 = os.path.abspath(input).split('/')[register_folder]
    
    lang0 = os.path.abspath(input).split('/')[lang_folder]
    
    return lang0, register0, status0

tot_wc = defaultdict(int)
tot_sents = defaultdict(int)
languages = ['en', 'ru'] # de

tot_bad = 0
tot_short = 0

for subdir, dirs, files in os.walk(rootdir):

    for i, file in enumerate(files):

        filepath = subdir + os.sep + file
        last_folder = subdir + os.sep

        lang_folder = len(os.path.abspath(last_folder).split('/')) - 1  # 'ru' # 'en', 'de'

        language = os.path.abspath(last_folder).split('/')[lang_folder]

        # data hierachy: /your/path/to/corpus/fiction/source/en/*.conllu

        # this collects counts for every sentence in a document
        # prepare for writing metadata:
        lang, reg, status = get_meta(last_folder)
        meta_str = '_'.join(get_meta(last_folder)) # lang, register, korp, status

#         if i % 20 == 0:
#             print('I have processed %s files from %s' % (i, meta_str.upper()), file=sys.stderr)

        # don't forget the filename
        doc = os.path.splitext(os.path.basename(last_folder + filepath))[0]  # without extention

        data = open(filepath).readlines()

        corp_id = lang + '_' + status + '_' + reg
        sents, bad, short = get_trees(data)
        tot_bad += bad
        tot_short += short
    
        normBy_wc = wordcount(sents)
        tot_wc[corp_id] += normBy_wc
        tot_sents[corp_id] += len(sents)

print('Word counts by subcorpus:')
for k, v in tot_wc.items():
    print(k, v)

print()
print("Number of sentences:")
for k, v in tot_sents.items():
    print(k, v)
    
print('Sentence splitting errors:', tot_bad)
print('Short sentences:', tot_short)