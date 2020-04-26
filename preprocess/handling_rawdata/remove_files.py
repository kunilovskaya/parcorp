# copy files on the list from one folder to another

import os, sys
import shutil
import pandas as pd

fns = '/home/u2/proj/regbalance/549translated_rbc.fns'  # список имен файлов
# из какой папки копировать файлы по именам в списке
dir_src = "/home/u2/proj/regbalance/lms/raw/media/ru_rncP/"

files = [f.strip() for f in os.listdir(dir_src) if f.endswith('.txt')]

count_done = 0
count_failed = 0
not_in_files = 0
copy_lst = [f.strip() for f in open(fns, 'r').readlines()]

to_remove = set(copy_lst)
print('Number in source folder:', len(files))
print(files[:3])
print('Number on list:', len(to_remove))
print(copy_lst[:3])

for f in to_remove:
    if f in files:
        try:
            os.remove(dir_src + f)
            count_done += 1
        except IOError:
            count_failed += 1
            # print('\t', f)
    else:
        not_in_files += 1
        # print('==', f)
print('Removed:', count_done)
print('On-list files absent from folder:', not_in_files)
print('Failed to remove matched file??', count_failed)

print("Finished!")
