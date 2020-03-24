#!/usr/bin/python
# coding: utf-8
# extract text segments <seg>text text</seg> from TMX into plaintext files for each language (en and ru) from
# https://transvision.mozfr.org/downloads/


import sys
from xml.dom import minidom
import os

OUT = 'mozilla_localise/'
os.makedirs(OUT, exist_ok=True)

argument = '/home/u2/resources/corpora/parallel/mozilla_en-US_ru_b1c0d54dec67ae189865fa6c33b9aad7_normal.tmx'

doc = minidom.parse(argument)
node = doc.documentElement
translation_units = doc.getElementsByTagName("tu")
en_segments = []
ru_segments = []
en_wc = 0
ru_wc = 0
en_shorts = 0

with open(OUT + 'en_localise.txt', 'w') as en_out, open(OUT + 'ru_localise.txt', 'w') as ru_out:
    for tu in translation_units:
        tuvs = tu.getElementsByTagName("tuv")
        
        for tuv in tuvs:
            text = tuv.getElementsByTagName('seg')[0].childNodes[-1].data
            lang = tuv.getAttributeNode('xml:lang').nodeValue
            if lang == 'en-US':
                en_segments.append(text)
            if lang == 'ru':
                ru_segments.append(text)
    for pair in zip(en_segments, ru_segments):
        if len(pair[0].split()) > 2 and len(pair[1].split()) > 2:
            en_wc += len(pair[0].split())
            ru_wc += len(pair[1].split())
            
            # print(pair[0], pair[1])
            en_out.write(pair[0] + '\n')
            ru_out.write(pair[1] + '\n')
        else:
            if len(pair[0].split()) <= 2:
                en_shorts += 1

print('Word count: EN %d, RU %d' % (en_wc, ru_wc))
print('Total number of sentence pairs %d' % len(en_segments))
print('Sources > 2', len(en_segments) - en_shorts)




