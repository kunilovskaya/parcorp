'''
calculate Wilcoxon's matched pairs test; input: matched values for two corpora, tab-separated

USAGE: python3 wilcoxson_paired.py my_stats.tsv
Example:
    python3 stats/wilcoxson_paired.py stats/tables/sent-length_stats.tsv
'''


import sys
import numpy as np
import scipy.stats


fname = sys.argv[1]

lst = open(fname,'r').readlines()

STfreqs = []
TTfreqs = []

for line in lst:
    res = line.strip().split('\t')
    (item, freq1, freq2) = res

    TTfreqs.append(float(freq1))
    STfreqs.append(float(freq2))
 
x = np.array(TTfreqs)
y = np.array(STfreqs)
print(len(x), len(y))

print(scipy.stats.wilcoxon(x, y, zero_method='pratt', correction=False))