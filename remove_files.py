# copy files on the list from one folder to another

import os, sys
import shutil
import pandas as pd

fns = 'en_discard_yandex_pairs.fns'   # список имен файлов
# из какой папки копировать файлы по именам в списке
dir_src = "yandex/pro/ru/"

files = [f.strip() for f in os.listdir(dir_src) if f.endswith('.txt')]

count_done = 0
count_failed = 0
not_in_files = 0
copy_lst = open(fns, 'r').readlines()

base_fns = list()
for line in copy_lst:
	line = line.strip()
	base_fns.append(line)
to_remove = set(base_fns)
print('Number in source folder:', len(files))
print(files[:3])
print('Number on list:', len(to_remove))
print(base_fns[:3])

for f in to_remove:
	if f in files:
	# lose extensions for matching purposes if necessary
	# if f.strip().split('.')[0] in base_fns:   # lose extensions for matching purposes
		# print(f)
		try:
			os.remove(dir_src + f)
			count_done += 1
		except IOError:
			count_failed += 1
			print('\t',f)
	else:
		not_in_files += 1
		print('==',f)
print('Removed:', count_done)
print('Files NOT found?:', not_in_files)
print('Errors:', count_failed)

print("Finished!")
