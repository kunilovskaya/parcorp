# coding: utf-8

# this module contains proprocessing functions: cleaning the texts, unifying characters and annotating with UDpipe
# set the lang to get the right UD model!!

import os
import re


def cleanhtml(raw_html):
    # get rid of fragmets of xml code
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def num_replace(word):
    # if selected, replaces 2019 with xxxx
    newtoken = 'x' * len(word)
    return newtoken

def clean_token(token, misc, lang=None):
    """
    :param token: the contents of the token field from each conllu line
    :param misc:  contents of "MISC" field in CONLLU
    :return: only valid tokens stripped of leading/trailing spaces
    """
    out_token = token.strip().replace(' ', '')
    if lang == 'ru':
        if token == 'Файл' and 'SpaceAfter=No' in misc:
            return None
    if lang == 'en':
        if token == 'File' and 'SpaceAfter=No' in misc:
            return None
    return out_token


def clean_lemma(lemma, pos):
    """
    :param lemma: the contents of the lemma field from each valid conllu line
    :param pos: the contents of the PoS field from each valid conllu line
    :return: filtered lemmas
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
            ('\t\n\r абвгдеёзжийклмнопрстуфхцчшщьыъэюяАБВГДЕЁЗЖИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ,.[]{}()=+-−*&^%$#@!?~;:0123456789§/\|"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')
    
    alphabet.append("'")
    
    allowed = set(currencies + alphabet)
    
    cleaned_text = [sym for sym in text if sym in allowed]
    cleaned_text = ''.join(cleaned_text)
    
    return cleaned_text

##### MOST FILTERING CAN BE SET UP HERE #############
# filter out selected token categories: punctuation, fuction words or stop words, etc
def check_word(token, pos, nofunc=None, nopunct=None, noshort=True, stopwords=None, lose_NUM=False):
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


def postprocess_ud(ud_annotated, outfile, sentencebreaks=True, entities=None, lang=None):
  
    if entities is None:
        entities = {'PROPN'}
        
    lempos0 = open(outfile, 'w')

    nr_lines = 0
    named = False
    memory = []
    mem_case = None
    mem_number = None

    content = [l for l in ud_annotated.split('\n') if not l.startswith('#')]
    for line in content:
        if not line.strip():
            if sentencebreaks:
                lempos0.write('\n')
            named = False
            if memory:
                past_lemma = '::'.join(memory)
                memory = []
                lempos0.write(past_lemma + '_PROPN ')

            continue
        res = line.strip().split('\t')
        if len(res) != 10:
            continue
        (word_id, token, lemma, pos, xpos, feats, head, deprel, deps, misc) = res
        nr_lines += 1
        token = clean_token(token, misc, lang=lang)
        cleaned_lemma = clean_lemma(lemma, pos)
        
        # if you want filtering pass keyworded params here: add lists or select True/False
        lemma = check_word(cleaned_lemma, pos, nofunc=None, lose_NUM=True)
        
        if not lemma and not token:
            continue
        if pos in entities:
            if '|' not in feats:
                # tagging unigram PROPN
                lempos0.write('%s_%s ' % (lemma, pos))
                continue
            morph = {el.split('=')[0]: el.split('=')[1] for el in feats.split('|')}
            if 'Case' not in morph or 'Number' not in morph:
                lempos0.write('%s_%s ' % (lemma, pos))
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
                    lempos0.write(past_lemma + '_PROPN ')
                    lempos0.write('\n')
            else:
                named = False
                past_lemma = '::'.join(memory)
                memory = []
                lempos0.write(past_lemma + '_PROPN ')
                lempos0.write('%s_%s ' % (lemma, pos))
        else:
            if not named:
                lempos0.write('%s_%s ' % (lemma, pos))
            else:
                named = False
                past_lemma = '::'.join(memory)
                memory = []
                lempos0.write(past_lemma + '_PROPN ')
                
                lempos0.write('%s_%s ' % (lemma, pos))
                
        if not sentencebreaks:
            if 'SpacesAfter=\\n' in misc or 'SpacesAfter=\s\\n' in misc:
                lempos0.write('\n')
    lempos0.close()
    

# the three functions below represent options for what one might want to have as the output of parsing: *.conllu, *.lempos, *.sent_tok
def do_conllu_only(pipeline, text, ud_outf):
    # lose xml
    # text = cleanhtml(text)
    
    # take care of inverted commas, bad symbols, currencies, emptylines, indents
    res = unify_sym(text.strip())

    # get the default conllu annotation
    ud_tagged = pipeline.process(res)
    
    with open(ud_outf, 'w') as udout:
        udout.write(ud_tagged)


def do_conllu2lempos(pipeline, text, ud_outf):
    
    res = unify_sym(text.strip())
    
    # get the default conllu annotation
    ud_tagged = pipeline.process(res)
    
    # write it to file
    with open(ud_outf, 'w') as udout:
        udout.write(ud_tagged)
        
    return ud_tagged
    