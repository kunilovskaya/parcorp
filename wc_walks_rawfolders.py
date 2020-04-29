# count words in texts in each subdir below rootdir

import os
from collections import defaultdict
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--root', default='parsing/clean/', help="Path to a folder (or a tree of folders) of prepared txt files", required=True)
parser.add_argument('--depth', default=3, type=int, help="Number of folder levels under root. Example: data/rltc/pro/ru/ depth under data =3", required=True)
args = parser.parse_args()

rootdir = args.root

tot_wc = defaultdict(list)
fns = defaultdict(list)
for subdir, dirs, files in os.walk(rootdir):

    for i, file in enumerate(files):

        filepath = subdir + os.sep + file
        my_cat = subdir.split('/')[-args.depth:]
        my_cat = '_'.join(my_cat)

        text = open(filepath).read()
        words = text.split()
        wc = len(words)
        tot_wc[my_cat].append(wc)
        fns[my_cat].append(file)

print('\t\tWords\tTexts')
for k, v in tot_wc.items():
    wc = np.sum(v)
    print('%s\t%s\t%s' % (k, wc, len(v)))
    
print('Done!')
