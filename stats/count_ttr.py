'''
Compare two plain text (lemmatised) corpora in one language
(ex. human vs machine translation or translation vs non-translations)
on type-to-token ratios averaged for each text
Mind that the texts need to be of comparable size!

USAGE: python3 count_ttr.py /path/to/corpus1/ /path/to/corpus2/
'''

import sys,codecs,os
import numpy as np
import scipy.stats as stats

corpus1 = sys.argv[1]
corpus2 = sys.argv[2]

ttrs1 = []
ttrs2 = []



files_corpus1 = [f for f in os.listdir(corpus1) if f.endswith('.txt')] # check your extension!
for f in files_corpus1:
    text = open(corpus1+f,'r').read()
    tokens = text.split()
    types = sorted(set(tokens))
    ttrs1.append(float(len(types))/len(tokens))

files_corpus2 = [f for f in os.listdir(corpus2) if f.endswith('.txt')] # check your extensions!
for f in files_corpus2:
    text = open(corpus2+f,'r').read()
    tokens = text.split()
    types = sorted(set(tokens))
    ttrs2.append(float(len(types))/len(tokens))


print('Average TTR for %s' % corpus1, np.mean(ttrs1))
print('Standard deviation for %s' % corpus1, np.std(ttrs1))
print()
print('Average TTR for %s' % corpus2, np.mean(ttrs2))
print('Standard deviation for %s' % corpus2, np.std(ttrs2))
print()
p = stats.ttest_ind(ttrs1,ttrs2)[1]
print('P value:', p)
