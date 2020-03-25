'''
TASK:
from one-sentence-per-line corpus (see en_tokenise_sentences.py) produce a tab-delimited list of filenames and average sentence lengths
before using make sure that you have filtered out sentence tokenisation errors!

USAGE: python3 count_sent-lengths.py /path/to/folder/
'''


from __future__ import division
import sys,os

arg1 = sys.argv[1]


corp = [f for f in os.listdir(arg1) if f.endswith('.conn')]
for f in corp:
    text = open(arg1+f,'r').readlines()
    words = 0
    sentences = len(text)
    for s in text:
        text_split = s.split()
        words += len(text_split)
    fstat = float(words)/sentences

    print(fstat, '\t', f)

    



