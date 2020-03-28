"""
TASK:
are the frequency distributions for an item (or cumulative freqs for a list of items) statistically different in two corpora (ex.human and machine translations)
If you want to apply this script to the corpora in two languages and your search items are lemmas, make sure that the list contains correspondences.
The script can be used to compare the freqs of universal tags, if your corpora are PoS represented or have lempos (ex. не_PART поддаваться_VERB соблазн_NOUN ._PUNCT).

The script extects paths to two plain text corpora and a list of queries.
It counts freqs for each item in each file of each corpus and applies two-tailed t-test to the resulting lists of values

USAGE: python3 /path/to/corpus1/ path/to/corpus2/ /path/to/searchlist.txt
"""

import sys,codecs,os
import numpy as np
import scipy.stats as stats

corpus1 = sys.argv[1]
corpus2 = sys.argv[2]
items = sys.argv[3]

query_list = set([w.strip() for w in open(items,'r').readlines()])

freqs_corpus1 = {e:[] for e in query_list}
freqs_corpus2 = {e:[] for e in query_list}

item_counts1 = []
files1 = [f for f in os.listdir(corpus1)]


for f in files1:
    text = open(corpus1 + f,'r').read()
    for i in query_list:
        freq = float(text.count(i))/len(text.split()) # frequency normalised to the text word count
        freqs_corpus1[i].append(freq)
  
        
files2 = [f for f in os.listdir(corpus2)]

for f in files2:
    text = open(corpus2 + f,'r').read()
    for i in query_list:
        freq = float(text.count(i))/len(text.split()) # frequency normalised to the text word count
        freqs_corpus2[i].append(freq)
        
print('Item\t%s average\t%s average\tP value according to t-test' % (corpus1.split('/')[-3],corpus2.split('/')[-3]))

for item in query_list:
    average1 = np.mean(freqs_corpus1[item])
    average2 = np.mean(freqs_corpus2[item])
    p = stats.ttest_ind(freqs_corpus1[item],freqs_corpus2[item])[1]
    print(item,'\t', average1, '\t', average2,'\t' , p)


