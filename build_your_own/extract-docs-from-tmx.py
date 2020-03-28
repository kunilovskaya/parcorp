# TASK: extract text segments <seg>text text</seg> from a standard TMX into plaintext files for each document in SL and TL (to be used in AntPConc


from xml.dom import minidom
import os
from collections import defaultdict

OUT = 'aligned_docs/'
os.makedirs(OUT, exist_ok=True)

parcorp = 'media_prof2018.tmx'

en_dict = defaultdict(list)
ru_dict = defaultdict(list)
count = 0

doc = minidom.parse(parcorp)
node = doc.documentElement
translation_units = doc.getElementsByTagName("tu")

for tu in translation_units:
    docs_pair = tu.getElementsByTagName("prop")[0].childNodes[-1].data
    tuvs = tu.getElementsByTagName("tuv")
    
    for tuv in tuvs:
        lang = tuv.getAttributeNode('xml:lang').nodeValue
        text = tuv.getElementsByTagName('seg')[0].childNodes[-1].data
        if lang == 'EN':
            en_segment = text
            en_dict[docs_pair].append(en_segment)
        elif lang == 'RU':
            ru_segment = text
            ru_dict[docs_pair].append(ru_segment)
        
for key in en_dict:
    en_list = en_dict[key]
    ru_list = ru_dict[key]
    
    fns = key.strip().split('-')
    with open(OUT + '%s.txt' % fns[0], 'w') as en_out, open(OUT + '%s.txt' % fns[1], 'w') as ru_out:
        for en, ru in zip(en_list,ru_list):
            en_out.write(en.strip() + '\n')
            ru_out.write(ru.strip() + '\n')
    count += 1
    
print('Number of paired docs written to files:', count)





