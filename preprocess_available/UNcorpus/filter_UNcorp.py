# coding: utf-8
# preprocessing raw text files extracted from UN corpus downloaded from https://conferences.unite.un.org/UNCORPUS/en/DownloadOverview#download
# manual inspection indicates that there are a lot of badly-split lines with no grammatical sentences at all
'''
delete all headings, lists of one word and figures (tables) and meta info
e.g. from 1995_cerd_c_263_add_4.txt
ОРГАНИЗАЦИЯ
ОБЪЕДИНЕННЫХ НАЦИЙ
CERD
МЕЖДУНАРОДНАЯ
КОНВЕНЦИЯ
О ЛИКВИДАЦИИ
ВСЕХ ФОРМ
РАСОВОЙ ДИСКРИМИНАЦИИ
Distr.
GENERAL
CERD/C/263/Add.4
'''

'''
TODO
8 ноября 1986 года Армения 13 сентября 1993 года а/ 13 декабря 1993 года Афганистан
10 January 1992 a/
13 September 1993 a/
'''

import os
import re

def fix_newlines(text):  # < text = open(arg+i, 'r').read()
    '''
    get unmotivated linebreaks
    '''
    matches = []
    
    pattern = r'([a-z,;-])\n([a-zA-Z])'  # returns a list of matches
    s = re.findall(pattern, text)
    clean = re.sub(r'::', '', text)
    clean = re.sub(r'➢ ', '', clean)
    cleantext = re.sub(r'( Prof.)\n([A-Z])', r'\1 \2', clean)
    if s:
        matches.append(s)
        ## re.sub() does replace all matches it finds
        cleanertext = re.sub(r'([a-z,:;-])\n([-a-zA-Z])', r'\1 \2',cleantext)  # adjust the ABC!!! заменяем немотивированные разрывы строк на пробел
        text_out = cleanertext
    else:
        text_out = text
    matches_flat = [item for items in matches for item in items]
    
    # print('BAD LINEBREAKS:', len(matches_flat))
    return text_out, len(matches_flat)


raw = '/home/u2/resources/corpora/parallel/UNv1.0-TEI/parallel/en/'
# parent directory
parent = os.path.join(raw, os.pardir)
outto = os.path.abspath(parent) + '/source/en/' # pro/ru/
os.makedirs(outto, exist_ok=True)

# lang = 'ru' # 'en'

wc = 0
short_texts = 0
badbr = 0
fh = [f for f in os.listdir(raw) if f.endswith('.txt')]

for file in fh:
    text_in = open(raw + file, 'r').read()
    text_out, badbreaks = fix_newlines(text_in)
    badbr += badbreaks
    this_file_wc = 0
    textlines = text_out.split('\n')
    # textlines = open(raw + file, 'r').readlines()
    with open(outto + file, 'w') as outfile:
        for line in textlines:
            if len(line.split()) >= 4:
                if re.search('[a-zA-Z]', line): # [а-яА-Я]
                    if not re.search('[àïðåëÿ]', line):
                        if not line.isupper():
                            if line.startswith('PART') or line.startswith('Article') or line.startswith('['):
                                continue
                            else:
                                this_file_wc += len(line.split())
                                wc += len(line.split())
                                outfile.write(line + '\n')
                                print(line)
        if this_file_wc < 400:
            short_texts += 1
            os.remove(outto+file)

print('Total tokens in ref', wc)
print('Number of short texts filered:', short_texts)
print('Number of badbreaks:', badbr)






