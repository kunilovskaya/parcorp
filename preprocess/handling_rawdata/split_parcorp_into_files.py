# creating a number of files from the yandex parallel corpus (corpus.en_ru.1m.en and aligned corpus.en_ru.1m.ru)
# USAGE: python3 /home/u2/proj/quest/process_news-commentary_en.py news-commentary-v15.en.gz ../en_news-comm_clean.txt en

import os
enOUT = 'yandex/source/en/'
ruOUT = 'yandex/pro/ru/'
os.makedirs(enOUT, exist_ok=True)
os.makedirs(ruOUT, exist_ok=True)
badend = 0
low = 0
short = 0
count = 0
filenums = 0
# lines_per_file = 500 # 2000 # for yandex parcorp # results in 1739 files (500 lines per file)
# lines_per_file = 350 # for mozilla parcorp
# lines_per_file = 350 # # for ru ref popsci
lines_per_file = 500

ensmallfile = None
rusmallfile = None
bigfile1 = open('/home/u2/tools/syncthing/rgcl/1mcorpus/corpus.en_ru.1m.en', 'r').readlines()
bigfile2 = open('/home/u2/tools/syncthing/rgcl/1mcorpus/corpus.en_ru.1m.ru', 'r').readlines()
for lineno, (enline, ruline) in enumerate(zip(bigfile1, bigfile2)):
    # add filtering for lowercase sentence starts and no sentence-end punctuation sentences
    if not enline.split()[-1].endswith('.') and not enline.split()[-1].endswith('!') and not enline.split()[-1].endswith('?') and not enline.split()[-1].endswith('...'): # just delete last lines in newly split files that do not end with a period
        print('Skipping:', enline)
        badend += 1
        continue
    # filter out lines starting with a lowecase char
    elif enline.split()[0].islower():
        print('Low start:', enline)
        low += 1
        continue
    elif len(enline.split()) < 4:
        short += 1
        continue
    else:
        print(enline)
        print(ruline)
        count += 1
    if lineno % lines_per_file == 0:
        print(count)
        filenums += 1
        if ensmallfile:
            ensmallfile.close()
        if rusmallfile:
            rusmallfile.close()
            
        en_small_filename = enOUT + 'en_yandex_%d.txt' % filenums
        ensmallfile = open(en_small_filename, "w")
        ru_small_filename = ruOUT + 'ru_yandex_%d.txt' % filenums
        rusmallfile = open(ru_small_filename, "w")
    ensmallfile.write(enline)
    rusmallfile.write(ruline)
if ensmallfile:
    ensmallfile.close()
if rusmallfile:
    rusmallfile.close()

print('Number of very short sentences:', short)
print('Bad ending lines skipped:', badend)
print('Lowercase starts filtered out:', low)
print('Total number of retained sentences', count)