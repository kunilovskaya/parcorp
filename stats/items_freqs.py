'''
TASK:
Given a list of targeted items, extract absolute and normalised frequencies from a one-sentence-per-line format
(1) of all list items in each file (corpus_stats.tsv)
(2) of each item in all corpus files (+ range) (items_stats.tsv)

The script ouputs two tsv files (by default to the working directory).

USAGE: python3 /path/to/corpus/ /path/to/items/list/
'''

import sys,os
import numpy as np
import scipy.stats as stats
import math


corpus = sys.argv[1]
items_list = sys.argv[2]

items = set([w.strip() for w in open(items_list,'r').readlines()])

hits_dict = {word:[] for word in items}
nfreq_dict = {word:[] for word in items}

files = [f for f in os.listdir(corpus)]
corp_size = 0
count = 0
allsents = 0

with open('stats/tables/functionals_corpus_stats.tsv', 'w') as corpus_stats:
    corpus_stats.write('file\t all hits\t sent-normed\t unseen-items\n')
    for f in files:
        unseen = []
        local_hits = 0
        text = open(corpus + f,'r').read()
        corp_size = corp_size + len(text.split())
        txt = open(corpus + f,'r').readlines()
        sents = len(txt)
        allsents = allsents + sents # total sentences in corpus
        count +=1
        for word in items:
            hits = text.count(word) # this methods gets all matches regardless word boundaries, which can be a problem!
            local_hits += hits
            if hits == 0:
                unseen.append(word)
            
            nfreq = float(hits/sents)  # normalized to the number of sents
            
            hits_dict[word].append(hits)
            nfreq_dict[word].append(nfreq)
            
        normed = local_hits/sents
        
        row = '%s\t%d\t%d\t%d' % (f, local_hits, normed, len(unseen))
        corpus_stats.write(row + '\n')
        
with open('stats/tables/functionals_items_stats.tsv', 'w') as items_stats:
    items_stats.write('item\t corpus-hits\t sents-normed \t range(%)\n')
    allhits = 0
    
    for word in items:
        total = sum(hits_dict[word])
        naverage = np.mean(nfreq_dict[word])
        allhits +=total
        coverage =0
        for v in hits_dict[word]:
            if v > 0:
                coverage +=1
        intext = coverage/count*100
        # ips = sum(hits_dict[word])/allsents*100 # an alternative way of producing item stats for a corpus
        
        row = '%s\t%d\t%s\t%d' % (word, total, naverage, intext)
        items_stats.write(row + '\n')
    
print('Corpus size (words): ', corp_size, file=sys.stderr)
print('Corpus size (sents): ', allsents, file=sys.stderr)
print('Number of texts: ', count, file=sys.stderr)
print()
print('Total hits for all listitems: ', allhits, file=sys.stderr)
print('Frequency normalised to corpus sentence count: %.3f' % (allhits/allsents), file=sys.stderr)