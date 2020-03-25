#! /usr/bin/python3

from yandex import Translater # install Translater from https://pypi.org/project/yandex-translater/

import os

tr = Translater()

tr.set_default_ui('ru')
tr.set_key('trnsl.1.1.20180blah-BLAH-blah')  # get your own free key here https://translate.yandex.com/developers/keys (press Create key)

tr.set_from_lang('en')
tr.set_to_lang('ru')

files = "/path/to/folder/with/texts/to/be/translated/" # provide a real path to the input texts
fh = [f for f in os.listdir(files) if f.endswith('.split')]

for f in fh:
	print(f)
	lines_in = open(files + f.strip(), 'r').readlines()
	file_out = open(files + f + '.yt', 'w') # the output texts with a different extension are stored to the input folder
	for line in lines_in:
		# try:
		tr.set_text(line)
		trans = tr.translate()
		print(trans)
		file_out.write(trans)

	
	file_out.close()

print("DONE")




# tr.set_text('text to translate')
# print(tr.translate())