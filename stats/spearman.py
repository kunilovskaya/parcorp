'''
Given values arranged in a tsv file, calculates Spearman rank correlation for two corpora based on common items (observations).
Spearman rank correlation is a non-parametric test that is used to measure the degree of association between two variables.

In the realm of Translation Studies:
(1) non-translation corpus frequency is the baseline (x), translation corpus frequencies is the "dependent" variable (y)
(2) freq of connectives/sentence length values in the source and translation of the same text

tsv formart: observation \t value1 \t value2

Examples:
(1) for corpora in the same language (translations vs non-translations; human vs machine-translation)
    comparing the use of listed generic Nouns:
        item       refs    translations
        people \t 0.0756 \t 0.0654
        building \t 0.0560 \t 0.0456
        ...
(2) for pairs sources and targets
    how correlated the sentence lengths/frequency of connectives are?
    file pair          ST        TT
    en_1.txt-ru_1.txt  0.5768    0.8777
    en_2.txt-ru_2.txt  0.5780    0.5678
    ...
USAGE: python3 spearman.py my_stats.tsv
Example:
    python3 stats/spearman.py stats/tables/sent-length_stats.tsv
'''

import sys
import scipy.stats as sc


stats_file = sys.argv[1]

def calculate(data):
    list1 = []
    list2 = []
    for line in data:
        res = line
        (freq1,freq2) = res
        list1.append(freq1)
        list2.append(freq2)
        
    a = sc.spearmanr(list1, list2) # a square matrix with length equal to len(list1) + len(list2)
    
    return a

d1 = open(stats_file,'r').readlines()

data = []

for line in d1:
    res = line.strip().split('\t')
    (item, freq1, freq2) = res
    data.append((float(freq1),float(freq2)))

a = calculate(data)
print('Spearman rho for observations in %s (and p-value for reference):' % stats_file)
print(a)
