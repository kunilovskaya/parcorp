#! python27
# -*- coding: utf-8 -*-
import os, sys, re
import numpy as np
from xml.dom import minidom

# извлекаю текст из xml Aranea и фильтрую его: длина текста, плохие начала и концы предложений

ol_file = '/home/u2/resources/corpora/aranea_ru_ar1520z.x0_26M' # aranea_ru_ar1520z.x0_26M, aranea_en_ar1400z.x0_16M
# lang = 'en'
res_to = 'aranea/ref/ru/' % lang
os.makedirs(res_to, exist_ok=True)

big = open(ol_file, 'r').read()
big0 = big.split('</doc>')
count = 0
count_long = 0
lengths = []

badend = 0
low = 0

for doc in big0:
        tokens = 0
        count += 1
        mysents = []
        pattern = re.compile(r'did="(\d+\.\d+)"')
        try:
                id = pattern.search(doc).group(1)
                print(id)
        except AttributeError:
                print("==broken id==")
                continue
        lines = doc.split('\n')
        wordlist = []
        for line in lines:
                if 'p>' in line or 's>' in line or '<g' in line or '/>' in line or '<doc' in line or '<p' in line:
                        continue
                else:
                        words = line.split('\t')
                        token = words[0]
                        tokens += 1
                        wordlist.append(token.strip())
        sent = ' '.join(wordlist)
        
        ## normalize inverted commas and apostrophes
        sent = re.sub(r'([„”“»«])', r'"', sent)
        sent = re.sub(r"([’´‘`])", r"'", sent)
        sent = re.sub(r'…', r'.', sent)
        # if you want to restore the punctuation to its untokenized variant
        sent = re.sub(r'\s+([?.!:;,%)])', r'\1', sent)
        sent = re.sub(r"\s?(')\s(?=[mtsd]\s)", r'\1', sent) ## he' s tall; I ' m fine; Roberta ' s(alas, this does not include followed by a dot or comma)
        sent = re.sub(r'([($£])+\s', r'\1', sent)
        ## special treatment for spaces with paired inverted commas
        sent = re.sub(r'"\s([A-ZА-Я0-9a-zа-я\s-]+)\s+"', r'"\1"', sent) ## this does not get everything but handles "... referred to as a "pushbike", "pedal bike", "pedal cycle", or "cycle"),
        # filter out lines not ending with .!?...
        if not sent.split()[-1].endswith('.') and not sent.split()[-1].endswith('!') and not sent.split()[-1].endswith('?') and not sent.split()[-1].endswith('...'): # just delete last lines in newly split files that do not end with a period
            print('Skipping:', sent)
            badend += 1
            continue
        # filter out lines starting with a lowecase char
        if sent.split()[0].islower():
            print('Low start:', sent)
            low += 1
            continue
        mysents.append(sent)
        ## skip files that are less that 400 words
        if tokens < 400:
                print(id,tokens)
                lengths.append(tokens)
                continue
        else:
                count_long += 1
                out = open(res_to + lang + '_' + id + '.txt', 'w')
                out.write(sent + '\n')
                out.close()
print(count, count_long)
# print(lengths)
print('Average text length %s' % np.average(lengths))
print('Corpus size: %s texts, %s tokens' % (count_long, np.sum(lengths)))
print('Bad ending lines skipped:', count)
print('Lowercase starts filtered out:', low)