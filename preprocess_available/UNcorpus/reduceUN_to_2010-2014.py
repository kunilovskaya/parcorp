# coding: utf-8
# filtered parallel EN>RU UN corpus counts 49M tokens on English side and 44M on Russian; the number of files is a bit mismatched, too
# this script limits the collection to paired by filenames texts only and to 2010-2014 only
# this measure is not required for the reference Russian non-translations, which counts 274 texts, 1M tokens and spans 1995-2014

import os
import shutil
from smart_open import open

sourcebig = '/home/u2/resources/corpora/parallel/UNv1.0-TEI/parallel/source/en_filtered_big/'
targetbig = '/home/u2/resources/corpora/parallel/UNv1.0-TEI/parallel/pro/ru_filtered_big/'
# parent directory
sparent = os.path.join(sourcebig, os.pardir)
tparent = os.path.join(targetbig, os.pardir)

s_outto = os.path.abspath(sparent) + '/en/'
os.makedirs(s_outto, exist_ok=True)
t_outto = os.path.abspath(tparent) + '/ru/'
os.makedirs(t_outto, exist_ok=True)
# lang = 'ru' # 'en'

wc = 0
unpaired = 0

fh1 = [f for f in os.listdir(sourcebig) if f.endswith('.txt')]
fh2 = [f for f in os.listdir(targetbig) if f.endswith('.txt')]

print(len(fh1) == len(fh2))
count = 0
s_tot = 0
t_tot = 0

for sfile in fh1:
    if 'ru_' + sfile[3:] in fh2:
        if '2010' in sfile or '2011' in sfile or '2012' in sfile or '2013' in sfile or '2014' in sfile: # '2009' in sfile add 3M tokens! and 800 textpairs
            count += 1
            source = sourcebig + sfile
            sourceto = s_outto + sfile
            s_wc = len((open(source).read()).split())
            s_tot += s_wc
            
            target = targetbig + 'ru_' + sfile[3:]
            targetto = t_outto + 'ru_' + sfile[3:]
            t_wc = len((open(target).read()).split())
            t_tot += t_wc
            if abs(s_wc - t_wc) < 50:
                shutil.copy(source, sourceto)
                shutil.copy(target, targetto)
            
print('Munber of textpairs:', count)
print(s_tot, t_tot)
print('DONE!')







