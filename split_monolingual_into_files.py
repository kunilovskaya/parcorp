# creating a number of files from a reference corpus
# for parallel corpus see a dedicated splitting option that processes sent pairs in parallel
import os
OUT = 'ref/ru/'
os.makedirs(OUT, exist_ok=True)

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