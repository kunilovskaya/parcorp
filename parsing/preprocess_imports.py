# coding: utf-8

## this module contains proprocessing functions: cleaning the texts, unifying characters and annotating with UDpipe
## set the lang to get the right UD model!!

import sys
import os
import wget
import re
from ufal.udpipe import Model, Pipeline
import time
import gzip


def tokeniseall(s, lang=None):
    # print('==IN (to tokenize)==', s)
    res0 = re.sub(r'(\d+),\s?(\d+)', r'\1\2', s)
    # print('==(0)==Sibstituted 58,000 with 58000 for it to be treated as ONE number, not TWO with a comma')
    punct = r'([\[\]\(\),\.-/":<>”?“!»«‒‖–‗—‘―’‚‛„†‡‰‱′″‴‵‶‷‸‹›¡¿+|’;%‘*=&°@ ~>§©$])'
    res = re.sub(punct, r' \1 ', res0)
    # print('\n==(1)==I have taken care of contracted forms both in frequency dictionary and in mixed transformations\n')
    # print('\n==(2)==I properly separate punctuation now, and keep only really important end-of-clause marks\n')
    if lang == 'ru':
        contract = ["'m", "'d", "'ll", "'re", "'s", "'ve"]
        search_for = re.compile("|".join(contract))
        res = search_for.sub(lambda x: ' ' + x.group(0), res)
    
    # print('==OUT (of tokenize)==', res2)
    return res  # this inserts a space before punctuation

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def num_replace(word):
    newtoken = 'x' * len(word)
    return newtoken


def clean_token(token, misc):
    """
    :param token:  токен (строка)
    :param misc:  содержимое поля "MISC" в CONLLU (строка)
    :return: очищенный токен (строка)
    """
    out_token = token.strip().replace(' ', '')
    
    if token == 'Файл' and 'SpaceAfter=No' in misc:
        return None
    return out_token


def clean_lemma(lemma, pos):
    """
    :param lemma: лемма (строка)
    :param pos: часть речи (строка)
    :return: очищенная лемма (строка)
    """
    out_lemma = lemma.strip().replace(' ', '').replace('_', '').lower()
    if '|' in out_lemma or out_lemma.endswith('.jpg') or out_lemma.endswith('.png'):
        pass
    if pos != 'PUNCT':
        if out_lemma.startswith('«') or out_lemma.startswith('»'):
            out_lemma = ''.join(out_lemma[1:])
        if out_lemma.endswith('«') or out_lemma.endswith('»'):
            out_lemma = ''.join(out_lemma[:-1])
        if out_lemma.endswith('!') or out_lemma.endswith('?') or out_lemma.endswith(',') \
                or out_lemma.endswith('.'):
            out_lemma = ''.join(out_lemma[:-1])
    return out_lemma


def list_replace(search, replacement, text):
    search = [el for el in search if el in text]
    for c in search:
        text = text.replace(c, replacement)
    return text


def unify_sym(text):  # принимает строку в юникоде
    text = list_replace \
        ('\u00AB\u00BB\u2039\u203A\u201E\u201A\u201C\u201F\u2018\u201B\u201D\u2019', '\u0022', text)
    
    text = list_replace \
        ('\u2012\u2013\u2014\u2015\u203E\u0305\u00AF', '\u2003\u002D\u002D\u2003', text)
    
    text = list_replace('\u2010\u2011', '\u002D', text)
    
    text = list_replace \
            ('\u2000\u2001\u2002\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u2060\u3000',
            '\u2002', text)
    
    text = re.sub('\u2003\u2003', '\u2003', text)
    text = re.sub('\t\t', '\t', text)
    
    text = list_replace \
            ('\u02CC\u0307\u0323\u2022\u2023\u2043\u204C\u204D\u2219\u25E6\u00B7\u00D7\u22C5\u2219\u2062',
            '.', text)
    
    text = list_replace('\u2217', '\u002A', text)
    
    text = list_replace('…', '...', text)
    
    text = list_replace('\u2241\u224B\u2E2F\u0483', '\u223D', text)
    
    text = list_replace('\u00C4', 'A', text)  # латинская
    text = list_replace('\u00E4', 'a', text)
    text = list_replace('\u00CB', 'E', text)
    text = list_replace('\u00EB', 'e', text)
    text = list_replace('\u1E26', 'H', text)
    text = list_replace('\u1E27', 'h', text)
    text = list_replace('\u00CF', 'I', text)
    text = list_replace('\u00EF', 'i', text)
    text = list_replace('\u00D6', 'O', text)
    text = list_replace('\u00F6', 'o', text)
    text = list_replace('\u00DC', 'U', text)
    text = list_replace('\u00FC', 'u', text)
    text = list_replace('\u0178', 'Y', text)
    text = list_replace('\u00FF', 'y', text)
    text = list_replace('\u00DF', 's', text)
    text = list_replace('\u1E9E', 'S', text)
    
    currencies = list \
            ('\u20BD\u0024\u00A3\u20A4\u20AC\u20AA\u2133\u20BE\u00A2\u058F\u0BF9\u20BC\u20A1\u20A0\u20B4\u20A7\u20B0\u20BF\u20A3\u060B\u0E3F\u20A9\u20B4\u20B2\u0192\u20AB\u00A5\u20AD\u20A1\u20BA\u20A6\u20B1\uFDFC\u17DB\u20B9\u20A8\u20B5\u09F3\u20B8\u20AE\u0192')
    
    alphabet = list \
            ('\t\n\r абвгдеёзжийклмнопрстуфхцчшщьыъэюяАБВГДЕЁЗЖИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ,.[]{}()=+-−*&^%$#@!~;:0123456789§/\|"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')
    
    alphabet.append("'")
    
    allowed = set(currencies + alphabet)
    
    cleaned_text = [sym for sym in text if sym in allowed]
    cleaned_text = ''.join(cleaned_text)
    
    return cleaned_text

# filter out some lempos cats
def check_word(token, pos, nofunc=None, nopunct=None, noshort=True, stopwords=None, lose_NUM=True):
    if lose_NUM:
        if pos == 'NUM' and token.isdigit():  # Replacing numbers with xxxxx of the same length
            token = num_replace(token)
    if nofunc:
        if pos in nofunc:
            return None
    if nopunct:
        if pos == 'PUNCT':
            return None
    
    if stopwords:
        if token in stopwords:
            return None
    if noshort:
        if len(token) < 2 and pos == 'X':
            return None
    
    return token

def postprocess_ud(ud_annotated, outfile, txt_sents_out, sentencebreaks=True, entities=None):
    """
    :param source_file:
    :param outfile:
    :param sentencebreaks:
    :param entities:
    :return:
    """
    if entities is None:
        entities = {'PROPN'}
    tempfile0 = open(outfile, 'w')

    nr_lines = 0
    named = False
    memory = []
    mem_case = None
    mem_number = None

    content = [l for l in ud_annotated.split('\n') if not l.startswith('#')]
    for line in content:
        if not line.strip():
            if sentencebreaks:
                tempfile0.write('\n')
            named = False
            if memory:
                past_lemma = '::'.join(memory)
                memory = []
                tempfile0.write(past_lemma + '_PROPN ')  # Lemmas and POS tags
                # print('NER Print1 (after sentencebreak):\t'+ past_lemma + '_PROPN ', file=sys.stderr)
            continue
        res = line.strip().split('\t')
        if len(res) != 10:
            continue
        (word_id, token, lemma, pos, xpos, feats, head, deprel, deps, misc) = res
        nr_lines += 1
        token = clean_token(token, misc)
        cleaned_lemma = clean_lemma(lemma, pos)
        lemma = check_word(cleaned_lemma, pos)
        
        if not lemma and not token:
            continue
        if pos in entities:
            if '|' not in feats:
                ## we are tagging unigram PROPN
                tempfile0.write('%s_%s ' % (lemma, pos))  # Lemmas and POS tags
                # print('Print2 (unigram PROPN):\t' + past_lemma + '_PROPN ', file=sys.stderr)
                continue
            morph = {el.split('=')[0]: el.split('=')[1] for el in feats.split('|')}
            if 'Case' not in morph or 'Number' not in morph:
                tempfile0.write('%s_%s ' % (lemma, pos))  # Lemmas and POS tags
                continue
            if not named:
                named = True
                mem_case = morph['Case']
                mem_number = morph['Number']
            if morph['Case'] == mem_case and morph['Number'] == mem_number:
                memory.append(lemma)
                if 'SpacesAfter=\\n' in misc or 'SpacesAfter=\s\\n' in misc:
                    named = False
                    past_lemma = '::'.join(memory)
                    memory = []
                    tempfile0.write(past_lemma + '_PROPN ')  # Lemmas and POS tags
                    # print('Print3 (guessed from grammatical coordination and default PROPN):\t' + past_lemma + '_PROPN ', file=sys.stderr)
                    tempfile0.write('\n')
            else:
                named = False
                past_lemma = '::'.join(memory)
                memory = []
                tempfile0.write(past_lemma + '_PROPN ')  # Lemmas and POS tags
                tempfile0.write('%s_%s ' % (lemma, pos))  # Lemmas and POS tags
        else:
            if not named:
                tempfile0.write('%s_%s ' % (lemma, pos))  # Lemmas and POS tags
            else:
                named = False
                ## I get the error on ruscorporawiki: TypeError: sequence item 0: expected str instance, NoneType found
                ### SOLVED see def clean_lemma(lemma, pos):
                past_lemma = '::'.join(memory)
                memory = []
                tempfile0.write(past_lemma + '_PROPN ')  # Lemmas and POS tags
                # print('Print4 (last print):\t' + past_lemma + '_PROPN ', file=sys.stderr)
                
                tempfile0.write('%s_%s ' % (lemma, pos))  # Lemmas and POS tags
        ## this produced empty lines between paragraphs in lempos, not it conllu, see EN_1_3 Credit out of control
        if 'SpacesAfter=\\n' in misc or 'SpacesAfter=\s\\n' in misc:
            tempfile0.write('\n')
    
    tempfile0.close()


def do_conllu_only(pipeline, text, lang, ud_outf):
    ## lose xml
    text = cleanhtml(text)
    ## take care of inverted commas, bad symbols, currencies, emptylines, indents
    res = unify_sym(text.strip())
    ## adding the tokenization routine to the good sentence
    ## this does not tokenise sentences!!
    res = tokeniseall(res, lang=lang)
    ## get the default conllu annotation
    ud_tagged = pipeline.process(text)
    
    ## the default settings for postprocessing in the internal check_word function:
    # nofunc=None, nopunct=None, noshort=True, stopwords=None
    ## tagging NER, replacing NUM, considering sentence-paragraphs breaks in the raw text
    ## skip short sentences
    with open(ud_outf, 'w') as udout:
        udout.write(ud_tagged)

def do_job(pipeline, text, lang, txt_outf, ud_outf, temp_outf, lempos_outf, txt_sents=True):
    
    ## lose xml
    text = cleanhtml(text)
    ## take care of inverted commas, bad symbols, currencies, emptylines, indents
    res = unify_sym(text.strip())
    ## adding the tokenization routine to the good sentence
    ## this does not tokenise sentences!!
    res = tokeniseall(res, lang=lang)
    if txt_sents == False:
        with open(txt_outf, 'w') as out:
            out.write(res)
    
    ## get the default conllu annotation
    ud_tagged = pipeline.process(text)
    
    ## the default settings for postprocessing in the internal check_word function:
    # nofunc=None, nopunct=None, noshort=True, stopwords=None
    ## tagging NER, replacing NUM, considering sentence-paragraphs breaks in the raw text
    ## skip short sentences
    with open(ud_outf, 'w') as udout:
        udout.write(ud_tagged)
    
    postprocess_ud(ud_tagged, temp_outf, txt_outf, sentencebreaks=txt_sents, entities=None)
    
    ## you want to skip short short and long sentences
    text = open(temp_outf, 'r')
    with open(lempos_outf, 'w') as lempos_ed:
        ### trying to delete empty lines
        for line in text:
            res = line.strip().split()
            if 4 <= len(
                    res) < 40:  ## see suggestions for data preprocessing http://www.statmt.org/wmt07/baseline.html referenced by FastText.py
                line = line.strip()
                lempos_ed.write(line)
                lempos_ed.write('\n')
    os.remove(temp_outf)
    
    # if you want to have a sentence- and word- tokenized txt
    if txt_sents == True:
        conllu = open(ud_outf, 'r').readlines()
        with open(txt_outf, 'w') as out:
            sentences = []
            current_sentence = []  # определяем пустой список
            for line in conllu:  # итерируем строки из обрабатываемого файла
                if line.strip() == '':  # что делать есть строка пустая:
                    if current_sentence:  # и при этом в списке уже что-то записано
                        # то добавляем в другой список sentences содержимое списка current_sentences
                        sentences.append(current_sentence)
                        ## voila! get your fully tokenized output!
                        ## this is where all words in the sentence are finally collected
                        tokenized = ' '.join([w[2] for w in current_sentence])
                        # print(tokenized, file=sys.stderr)
                        out.write(tokenized + '\n')
                        
                    current_sentence = []  # обнуляем список
            
                    # if the number of sents can by divided by 1K without a remainder.
                    # В этом случае, т.е. после каждого 1000-ного предложения печатай месседж. Удобно!
                    if len(sentences) % 1000 == 0:
                        print('I have already read %s sentences' % len(sentences), file=sys.stderr)
                    continue
                if line.strip().startswith('#'):
                    continue
                res = line.strip().split('\t')
                (identifier, token, lemma, upos, xpos, feats, head, rel, misc1, misc2) = res
                if '.' in identifier:  # ignore empty nodes possible in the enhanced representations
                    continue
                # во всех остальных случаях имеем дело со строкой по отдельному слову
                current_sentence.append((int(identifier), int(head), token, rel))
 

    lempos_ed.close()