'''
requires the installation of googletrans-2.4.0
USAGE:
python3 googletrans_api.py /path/to/folder/with/texts/to/be/translated/ /where/to/save/translation/
the error Expecting value: line 1 column 1 (char 0) is caused by the character limit of 15K in Googletrans API that a user is allowed free.
'''

from googletrans import Translator
import os, sys

translator = Translator(service_urls=['translate.google.ru']) # choose specific, seversl or no domain

source = sys.argv[1] # you can hard-code your path and call the script as python3 create_corpus.py
target = sys.argv[2]

fh = [f for f in os.listdir(source) if f.endswith('.txt')]
os.makedirs(target, exist_ok=True)

errors = 0
for f in fh:
    lines_in = open(source + f, 'r').readlines()
    print(f, len(lines_in))
    file_out = open(target + f + '.gt', 'w')
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


