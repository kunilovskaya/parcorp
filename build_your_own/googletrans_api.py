# installed googletrans-2.4.0

from googletrans import Translator
import os

translator = Translator(service_urls=['translate.google.ru']) # choose specific, seversl or no domain

files = "/path/to/folder/with/texts/to/be/translated/"

fh = [f for f in os.listdir(files) if f.endswith('.txt')]
outto = 'google_translated/'
os.makedirs(outto, exist_ok=True)

errors = 0
for f in fh:
	lines_in = open(files + f.strip(), 'r').readlines()
	file_out = open(outto + f + '.gt', 'w')
	for line in lines_in:
		try:
			trans = translator.translate(line, src='en', dest='ru')
			file_out.write(trans.text + '\n')

		except Exception as ex:
			errors += 1
			print(line)
			print(ex)
		# print(trans.text)

	file_out.close()

print("DONE")
print(errors)


# test whether it works
# print(translator.translate('veritas lux mea', src='en', dest='ru'))
# translations = translator.translate(['The quick brown fox', 'jumps over', 'the lazy dog'], dest='ru')
#
# for translation in translations:
# 	print(translation.origin, ' -> ', translation.text)


