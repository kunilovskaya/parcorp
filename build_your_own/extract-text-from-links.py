# author: kunilovskaya, April 2018

#use requests and justext to extract text from a list of URL and save them as plain texts

import requests, justext
import sys, os

#give the script a list of links to pages with text you want to include into your DIY-corpus
urls = sys.argv[1]

# create the output folder in the project working directory
output = 'from-links/'
outdir = os.makedirs(output, exist_ok=True)

def gettext4url(url, lang, fname):
    with open(fname, 'w') as outfile:
        response = requests.get(url)
        print(url)
        paragraphs = justext.justext(response.content, justext.get_stoplist(lang), max_link_density=0.5, length_low=50, \
                                     stopwords_high=0.3, stopwords_low=0.25)
        for paragraph in paragraphs:
            if not paragraph.is_boilerplate:
                print(paragraph.text)
                outfile.write(paragraph.text + '\n')

links = open(urls, 'r').readlines()
num = 1
for link in links:
    num += 1
    print(link, num)
    gettext4url(link.strip(), 'English', output+'en_'+str(num)+'.txt')
