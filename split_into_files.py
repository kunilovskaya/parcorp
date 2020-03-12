# creating a number of files from the yandex parallel corpus (corpus.en_ru.1m.en and aligned corpus.en_ru.1m.ru)
import os
OUT = 'ref/ru/'
os.makedirs(OUT, exist_ok=True)

# lines_per_file = 2000 # for yandex parcorp
# lines_per_file = 350 # for mozilla parcorp
lines_per_file = 494 # for ru ref popsci

smallfile = None
with open('onebig_ref_popsci.txt') as bigfile:
    for lineno, line in enumerate(bigfile):
        if lineno % lines_per_file == 0:
            if smallfile:
                smallfile.close()
            small_filename = OUT + 'ref_popsci_{}.txt'.format(lineno)
            smallfile = open(small_filename, "w")
        smallfile.write(line)
    if smallfile:
        smallfile.close()