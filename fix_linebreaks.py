# TASK:
# (3) find two consequtive lines where the first ends, and the other starts with lowercase
# (\n before or between lowcase char with no punctuation

# works May 10, 2019


import sys, os
import re


def fix_newlines(text): # < text = open(arg+i, 'r').read()
	'''
	get unmotivated linebreaks
	'''
	matches = []
	
	pattern = r'([а-я,;-])\n([а-яА-Я])' # returns a list of matches
	s = re.findall(pattern, text)
	
	if s:
		matches.append(s)
		## re.sub() does replace all matches it finds
		cleantext = re.sub(r'([а-я,;-])\n([а-яА-Я])', r'\1 \2', text)  # adjust the ABC!!! заменяем немотивированные разрывы строк на пробел
		text_out = cleantext
	else:
		text_out = text
	matches_flat = [item for items in matches for item in items]
	
	print('BAD LINEBREAKS:', len(matches_flat))
	return text_out
