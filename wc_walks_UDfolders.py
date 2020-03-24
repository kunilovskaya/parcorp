## print research corpus stats based on UD annotated data

import os, sys
from collections import defaultdict

rootdir = "/home/u2/resources/corpora/parcorp_register-balanced_parsed/"


def wordcount(trees):
    words = 0
    for tree in trees:
        words += len(tree)

    return words

def get_trees(data): # data is one object: a text or all of corpus as one file
    sentences = []
    only_punct = []
    current_sentence = []  # определяем пустой список
    for line in data:  # fileinput.input():  # итерируем строки из обрабатываемого файла
        if line.strip() == '':  # что делать есть строка пустая (это граница предложения!):
            if current_sentence:  # и при этом в списке уже что-то записано
                sentences.append(current_sentence)
            # if only_punct:
            # 	# if set(only_punct) == 2:
            # 		print('GOTCHA', only_punct)
            current_sentence = []  # обнуляем список
            only_punct = []
            # if the number of sents can by divided by 1K without a remainder.
            # В этом случае, т.е. после каждого 1000-ного предложения печатай месседж. Удобно!
            #         if len(sentences) % 1000 == 0:
            #             print('I have already read %s sentences' % len(sentences))
            continue
        if line.strip().startswith('#'):
            continue
        res = line.strip().split('\t')
        (identifier, token, lemma, upos, xpos, feats, head, rel, misc1, misc2) = res
        if '.' in identifier or '-' in identifier:  # ignore empty nodes possible in the enhanced representations
            continue
        # во всех остальных случаях имеем дело со строкой по отдельному слову
        # in ref_RU data there are sentences that consist of 4 PUNCTs only!
        for i in res:
            # print(res)
            only_punct.append(res[3])
        var = list(set(only_punct))
        # throw away sentences that consist of just PUNCT, particularly rare 4+ PUNCT
        if len(var) == 1 and var[0] == 'PUNCT':
            # print('GOTCHA', set(only_punct))
            continue
        else:
            current_sentence.append((int(identifier), token, lemma, upos, xpos, feats, int(head), rel))
    ## это записывает последнее предложение, не заканчиающееся пустой строкой? НЕЕЕТ, там есть пустая строка
    if current_sentence:
        # if len(current_sentence) < 3:
        # 	print('+++', current_sentence)
        sentences.append(current_sentence)  # получаем список предложений из файла

    sentences = [s for s in sentences if len(s) >= 4] ### here is where I filter out short sents
    # print('==', len(sentences))
    return sentences


# In[38]:


def get_meta(input):
    #/home/masha/02targets_wlv/data/croco/pro/de
    # prepare for writing metadata
    lang_folder = len(os.path.abspath(input).split('/')) - 1
    status_folder = len(os.path.abspath(input).split('/')) - 2
    korp_folder = len(os.path.abspath(input).split('/')) - 3

    status0 = os.path.abspath(input).split('/')[status_folder]
    korp0 = os.path.abspath(input).split('/')[korp_folder]
    # register0 = os.path.abspath(input).split('/')[reg_folder]
    lang0 = os.path.abspath(input).split('/')[lang_folder]

    return lang0,korp0,status0 ##register0,


# In[39]:


tot_wc = defaultdict(int)
languages = ['en', 'de', 'ru']

for subdir, dirs, files in os.walk(rootdir):

    for i, file in enumerate(files):

        filepath = subdir + os.sep + file
        last_folder = subdir + os.sep

        lang_folder = len(os.path.abspath(last_folder).split('/')) - 1  # 'ru' # 'en', 'de'

        language = os.path.abspath(last_folder).split('/')[lang_folder]

        # data hierachy: /your/path/ol/croco/pro/de/*.conllu

        # this collects counts for every sentence in a document
        # prepare for writing metadata:
        lang, korp, status = get_meta(last_folder)
        meta_str = '_'.join(get_meta(last_folder)) # lang, register, korp, status

#         if i % 20 == 0:
#             print('I have processed %s files from %s' % (i, meta_str.upper()), file=sys.stderr)

        # don't forget the filename
        doc = os.path.splitext(os.path.basename(last_folder + filepath))[0]  # without extention

        data = open(filepath).readlines()

        corp_id = lang + '_' + status + '_' + korp
        sents = get_trees(data)
        
        normBy_wc = wordcount(sents)
        tot_wc[corp_id] += normBy_wc
    

for k, v in tot_wc.items():
    print(k, v)

