'''
TASK:
from one-sent-per-line corpus of doc-level aligned ST and TT
produce a list of average sentence lengths with tab-delimited filenames for correlation analysis

USAGE: python3 count_sent-lengths.py /path/to/sources/ /path/to/targets/
Example: python3 stats/count_sent-lengths.py rawdata/mock_data/media/source/en/ rawdata/mock_data/media/pro/ru/
'''

# from __future__ import division #по умолчанию при делении 2/345 выдаем нецелые числа (хотя для этого есть float(), но почему-то ниже он выдаёт результат truncated to 0.0)
import sys, os

sources = sys.argv[1]
targets = sys.argv[2]

s_files = [f for f in os.listdir(sources)]
t_files = [f for f in os.listdir(targets)]

s_dict = {}
for f in s_files:
    print(f.strip()[2:])
    text = open(sources + f,'r').readlines()
    words = 0
    sentences = len(text)
    for s in text:
        text_split = s.split()
        words += len(text_split)
        
    length = words/sentences
    s_dict[f.strip()[2:]] = length # matching the docs in the pair on filename convensions: en(_1.txt) ru(_1.txt)
    

t_dict = {}
for f in t_files:
    text = open(targets + f, 'r').readlines()
    words = 0
    sentences = len(text)
    for s in text:
        text_split = s.split()
        words += len(text_split)

    length = words/sentences
    t_dict[f.strip()[2:]] = length

with open('stats/tables/sent-length_stats.tsv', 'w') as out:
    for key in s_dict:
        s_length = s_dict[key]
        t_length = t_dict[key]
        
        row = '%s\t%f\t%f' % (key,s_length,t_length)
        out.write(row + '\n')
    






