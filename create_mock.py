# TASK: copy first five files in each folder of a folder structure to a mock-data folder structure
# USAGE: python3 create_corpus.py /path/to/corpus/tree/of/folders/

import os, sys
import shutil

source_root = sys.argv[1] # you can hard-code your path and call the script as python3 create_corpus.py
target_root = 'formats/mock_tq_corpus_lempos/'

for subdir, dirs, files in os.walk(source_root):
    counter = 0
    for i, file in enumerate(files):
        
        filepath = subdir + os.sep + file
        my_relative_path = '/'.join((subdir + os.sep).split('/')[-4:-1])
        outto = target_root + '/' + my_relative_path + '/'
        os.makedirs(outto, exist_ok=True)
        # print(my_relative_path)
        if counter <= 5:
            shutil.copy(filepath, outto)
            counter += 1
        else:
            break
print('Success! Your mock corpus is ready!')

