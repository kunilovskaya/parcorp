# coding: utf-8

## count words in texts in each subdir below root

import os, sys
from collections import defaultdict
import numpy as np
import csv

rootdir = "data/"

tot_wc = defaultdict(list)
fns = defaultdict(list)
for subdir, dirs, files in os.walk(rootdir):

    for i, file in enumerate(files):

        filepath = subdir + os.sep + file
        my_cat = (subdir + os.sep).split('/')[-3:-1]
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