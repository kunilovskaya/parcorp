# copy files on the list from one folder to another

import os, sys
import shutil
import pandas as pd

fns = 'reduce_araneum_to_902texts.fns'   # список имен файлов
# из какой папки копировать файлы по именам в списке
dir_src = "/home/u2/resources/corpora/ru_aranea_4,9Ktexts_clean/ref/ru/"
# куда их копировать
outto = '/home/u2/yandexweb_source-pro-big-araneum-ref_raw/ref/'
os.makedirs(outto, exist_ok=True)
files = [f.strip() for f in os.listdir(dir_src) if f.endswith('.txt')]

count_done = 0
count_failed = 0

copy_lst = open(fns, 'r').readlines()

base_fns = list()
for line in copy_lst:
	line = line.strip()
	base_fns.append(line)
	
print('Number in source folder:', len(files))
print(files[:3])
print('Number on list:', len(base_fns))
print(base_fns[:3])

for f in files:
	if f in base_fns:
	# lose extensions for matching purposes if necessary
	# if f.strip().split('.')[0] in base_fns:   # lose extensions for matching purposes
		# print(f)
		try:
			shutil.copy(dir_src + f, outto)
			count_done += 1
		except IOError:
			count_failed += 1
			print(f)
	else:
		count_failed += 1

print('Copied:', count_done)
print('Files NOT copied: ')
print(count_failed)
print("Finished!")
