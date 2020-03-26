# copy files on the list from one folder to another

import os, sys
import shutil
import pandas as pd

fns = 'reduce_araneum_to_comparable_texts.fns'   # список имен файлов
# из какой папки копировать файлы по именам в списке
dir_src = "/home/u2/resources/corpora/araneum/ref/ru/"
# куда их копировать
outto = 'yandex/ref/ru/'
os.makedirs(outto, exist_ok=True)
files = [f.strip() for f in os.listdir(dir_src) if f.endswith('.txt')]

count_done = 0
count_failed = 0
not_in_files = 0
copy_lst = open(fns, 'r').readlines()

base_fns = list()
for line in copy_lst:
	line = line.strip()
	base_fns.append(line)
to_copy = set(base_fns)
print('Number in source folder:', len(files))
print(files[:3])
print('Number on list:', len(to_copy))
print(base_fns[:3])

for f in to_copy:
	if f in files:
	# lose extensions for matching purposes if necessary
	# if f.strip().split('.')[0] in base_fns:   # lose extensions for matching purposes
		# print(f)
		try:
			shutil.copy(dir_src + f, outto)
			count_done += 1
		except IOError:
			count_failed += 1
			print('\t',f)
	else:
		not_in_files += 1
		print('==',f)
print('Copied:', count_done)
print('Files NOT found?:', not_in_files)
print('Errors:', count_failed)

print("Finished!")
