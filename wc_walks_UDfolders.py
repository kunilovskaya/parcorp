"""
print research corpus stats for UD annotated data, for each subcorpus

Usage:
python3 wc_walks_UDfolders.py --root /path/to/folder/ --depth 2
"""



import os, sys
from collections import defaultdict

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--root', help="Path to a folder (or a tree of folders) of prepared txt files", required=True)
parser.add_argument('--depth', default=3, type=int, help='Depth of the folder structure under rootdir. Example: for clean/ted/ref/ru/ depth=3')
args = parser.parse_args()

rootdir = args.root

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

tot_wc = defaultdict(int)
tot_sents = defaultdict(int)
languages = ['en', 'ru']

tot_bad = 0
tot_short = 0

for subdir, dirs, files in os.walk(rootdir):

    for i, file in enumerate(files):

        filepath = subdir + os.sep + file
        path_to_last_folder = subdir
        corp_id = "_".join(path_to_last_folder.split('/')[-args.depth:])

        data = open(filepath).readlines()

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
print('Number of sentences:')
for k, v in tot_sents.items():
    print(k, v)
    
print('Sentence splitting errors:', tot_bad)
print('Short sentences:', tot_short)
