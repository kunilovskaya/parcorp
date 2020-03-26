'''
The script pulls the content of the 3d column from the treetagger output and produces a lemmatised text, which is all lowercased and all punctuation-separated.
Before using this script make sure you got rid of <unknown>. For  Danish, Polish and Russian it is recommended to use CSTlemma

USAGE: python3 lemmatise_ttagged.py /path/to/a/folder/of/files/*.ttagged
'''

import codecs, sys, os

argument = sys.argv[1]

fh = [f for f in os.listdir(argument) if f.endswith('.ttagged')]

outto = '/where/you/want/it/'
os.makedirs(outto, exist_ok=True)

for f in fh :
    lines = open(argument + f, 'r').readlines()
    out = open(argument + 'lemma/' + f + '.lemmas', 'w')
    
    for line in lines :
        data = line.split()
        try :
            lemma = data[2].strip() # if you set the number here to 3 you will get a PoS-represented corpus
        except : continue

        out.write(lemma + ' ')
    out.close() 
print("See lemmatised output")
