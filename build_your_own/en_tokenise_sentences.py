'''
TASK:
produce one-sentence per-line format from clean texts
requires NLTK
USAGE: python3 en_tokenise_sentences.py /path/to/folder/
'''


from __future__ import division
import sys, os
import nltk.data

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # adjust for other languages

argument = sys.argv[1]

outto = '/where/you/want/it/split/'
os.makedirs(outto, exist_ok=True)

abbrev = {'i.e', 'e.g', 'ca', 'sic', 'p', 'P', 'Mr', 'Mrs', 'Dr', 'Prof', 'ex', 'cf', 'Mt', 'Jan'} #adjust for other languages

sentence_tokenizer._params.abbrev_types.update(abbrev)
print("hello! sentence tokenisation in progress")


def sentence_splitter(text):
	return sentence_tokenizer.sentences_from_text(text.strip(), realign_boundaries=True)


files = [f for f in os.listdir(argument) if f.endswith('.txt')]  # adjust file extension appropriately!
num_files = 0
for f in files:
	num_files += 1
	print(f)
	text = open(argument + f, 'r').readlines()
	punct = ('.', '!', '?', '...')
	out = open(outto + f + '.split', 'a')
	for line in text:
		res = line.strip()
		sentences = sentence_splitter(res)
		for s in sentences:
			if not s.endswith(punct):
				s = s + '.'
			out.write(s.strip() + '\n')
	out.close()
print(str(num_files) + " files successfully split and written to the original folder with the different extention (*.split)")
