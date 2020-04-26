# this is a collection of text preprocessing tools
import re
import nltk.data

def sent_filter(s, min=None, max=None, lang=None):
    if lang == 'en':
        pattern1 = r'^[a-z]'  # line starts with lowercase char
        pattern2 = r'^By [A-Z][a-z]+ [A-Z]'
        
    if lang == 'ru':
        pattern1 = r'^[а-я]'  # line starts with lowercase char
        pattern2 = r'^[А-Я][а-я]+ [А-Я][а-я]+\.?\n'  # this is unnecessary if we delete lines shorter that 4 words anyway
        
    if max < len(s.split()) or len(s.split()) < min:  # bad sentence length
        
        return None
    
    else:
        s0 = re.search(pattern1, s)
        s1 = re.search(pattern2, s)
        
        if s0 == None and s1 == None:
            
            return s
        
        else:
            
            return None
        
def sent_splitter(text, lang=None):
    if lang == 'ru':
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/russian.pickle')
        abbrev = {u'т.н', u'т. н', u'т.п', u'т. п', u'п', u'корр', u'р', u'Спец', u'ул', u'гр', u'корп',
                  u'тыс', u'долл', u'руб', u'куб', u'т.е', u'т. е', u'ст', u'кв', u'ч', u'м', u'млн', u'млрд', u'Дж',
                  u'У', u'с', u'стр', u'кн', u'Кн', u'св', u'Св', u'см', u'?!', u'!!!', u'К', u'т.к', u'т. к', u'гг', u'вв',
                  u'дол', u'трлн', u'долл', u'напр', u'рис', u'греч', u'гос', u'В', u'млн', u'перев', u'н.э', u'т.д', u'т. д', u'г',
                  u'зам', u'Проф', u'Прим', u'прим', u'проф', u'франц', u'букв', u'проч', u'!!', u'англ', u'А', u'Б', u'В',
                  u'Г',  u'Д', u'Е', u'З', u'И', u'К', u'Л', u'М', u'Н', u'О', u'П', u'Р', u'С', u'Т', u'У',
                  u'Ф', u'Х', u'Э', u'Ю', u'Я', u'Дж', u'...', u'..', u'ред', u'№', u'англ', u'др', u'etc'}
        
    elif lang == 'en':
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        abbrev = {'&Co', 'AUG', 'Adm', 'Ala', 'Ald', 'App.Cas', 'Ariz', 'Ark', 'Assn', 'Assoc', 'Att', 'Aug', 'Av',
                  'Ave',
                  'Bancorp', 'Bde', 'Bhd', 'Blvd', 'Brig', 'Bros', 'C.-in-C', 'CO', 'CORP', 'COS', 'Ca', 'Calif',
                  'Canada-U.S', 'Canadian-U.S', 'Capt', 'Cas', 'Ch', 'Ch.App', 'Ch.D', 'Cia', 'Cie', 'Cm', 'Cmd',
                  'Cmnd', 'Co', 'Col', 'Colo', 'Conn', 'Corp', 'Cos', 'Cowp', 'Cr.App.R', 'Crim.L.R', 'D-Mass',
                  'D.Litt', 'D.Phil', 'DFl', 'Dec', 'Del', 'Dep', 'Dept', 'Deut', 'Diod', 'Div', 'Dr', 'Drs', 'Dtr',
                  'Durn', 'E.g', 'ESQ', 'Eph', 'Eq', 'Eqn', 'Eqns', 'Esq', 'Etc', 'Exch', 'Exod', 'Ext', 'FIG', 'Fam',
                  'Feb', 'Fig', 'Figs', 'Fla', 'Ft', 'G.m.b.H', 'Ga', 'Gen', 'Gov', 'Hdt', 'Hon', 'INC', 'Ibid', 'Ill', 'Inc',
                  'Ind', 'InfoCorp', 'Intercorp', 'Invest', 'JJ', 'JR', 'Jan', 'Japan-U.S', 'Jr', 'Jud', 'Kan',
                  'Korean-U.S', 'Ky', 'L.JJ', 'L.R.Ir', 'LL.M', 'LTD', 'La', 'Lt', 'Lt.-Col', 'Ltd', 'Ltda', 'M.Ed', 'M.Litt',
                  'M.Phil', 'Maj', 'Mass', 'Md', 'Me.T.A', 'Messrs', 'Mfg', 'Mich', 'Minn', 'Miss', 'Mo', 'Mod.Rep', 'Mont',
                  'Mr', 'Mrs', 'Ms', 'Neb', 'Nev', 'No', 'Non-U.S', 'Nos', 'Nov', 'Oct', 'Oe', 'Okla', 'Ont', 'Op',
                  'Ore', 'P.o.s', 'Pa', 'Ph', 'Ph.D', 'Pp', 'Prev', 'Prof', 'Prop', 'Pte', 'Ptr', 'Pty', 'Reg', 'Regt',
                  'Rep', 'Reps', 'Repub', 'Ret', 'Rev', 'Rom', 'S.p.A', 'Sec', 'Sen', 'Sens', 'Sept', 'Sgt', 'Sh.Ct',
                  'Sino-U.S', 'Soc', 'Som', 'Soviet-U.S', 'Sp', 'Sr', 'St', 'Ste', 'Suff', 'Syll', 'T.B.G.A.S', 'Tenn',
                  'Tex', 'Thess', 'Thuc', 'Transp', 'Trop', 'U.S.-U.K', 'U.S.-U.S.S.R', 'U.S.P.G.A', 'Univ', 'V.-C',
                  'Va', 'Vict', 'Vol', 'Vt', 'W.Va', 'Wash', 'Wis', 'Wyo', 'a-Ex-dividend', 'a.c', 'a.g.m', 'a.k.a', 'a.m',
                  'al', 'anti-U.S', 'approx', 'b.s', 'bldg', 'c.c', 'c.c.d', 'c.e.o', 'c.f', 'c.g', 'c.v', 'c/s', 'cap', 'cf',
                  'ch', 'cit', 'clar', 'co', 'col', 'cols', 'constr', 'cp', 'cwt', 'd.c', 'd.f', 'd.i.l', 'd.p.c', 'def',
                  'dw', 'e-Estimated', 'e.g', 'e.m.f', 'e.p.s.p', 'edn', 'edns', 'est', 'etc', 'ex-L.C.C', 'fig', 'fl',
                  'fol', 'ft', 'gen', 'govt', 'h.p', 'hon', 'hrs', 'i.c', 'i.e', 'ibid', 'inc', 'incl', 'juv', 'k.p.h',
                  'l.e.d', 'lbs', 'loc', 'm.d', 'm.p.h', 'msec', 'n.d', 'n.m.r', 'non-U.K', 'non-U.S', 'norw', 'nos',
                  'oz', 'ozs', 'p', 'p.a', 'p.c', 'p.m', 'p.o.s', 'p.p.m', 'p.s.i', 'p.w', 'pl', 'pls', 'pos', 'pp', 'pres',
                  'president-U.S', 'pro-U.S', 'q.v', 'qq.v', 'r.f', 'r.h', 'r.m.s', 'r.m.s.d', 'r.p.m', 'r.s.s', 'ref',
                  's', 's.a', 's.a.e', 's.d', 's.e.m', 's.r.l', 's.t.p', 'spp', 'sq.ft', 'sq.m', 'subss', 'v', 'v.B',
                  'v.w', 'var', 'viz', 'vol', 'vols', 'vs', 'w.c', 'ca', 'sic', 'p', 'P', 'ex', 'cf', 'Mt'}
    else:
        sentence_tokenizer = None
        abbrev = None

    sentence_tokenizer._params.abbrev_types.update(abbrev)
    
    return sentence_tokenizer.sentences_from_text(text.strip(), realign_boundaries=True)


def list_replace(search, replacement, text):
    search = [el for el in search if el in text]
    for c in search:
        text = text.replace(c, replacement)
    return text


def unify_sym(text):  # принимает строку в юникоде
    
    text = list_replace \
        ('\u00AB\u00BB\u2039\u203A\u201E\u201A\u201C\u201F\u2018\u201B\u201D\u02EE', '\u0022',
         text)  # neutral quotation mark \u0022
    
    text = list_replace \
        ('\u2012\u2013\u2014\u2015\u203E\u0305\u00AF', '\u2003\u002D\u002D\u2003', text)  # --
    
    text = list_replace('\u2010\u2011', '\u002D', text)  # hyphen or minus sign
    
    text = list_replace('\u2019\u02BC', "\u0027", text)  # neutral single quotation mark \u0027
    
    text = list_replace \
        ('\u2000\u2001\u2002\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u2060\u3000',
         '\u2002', text)  # EN SPACE
    
    text = re.sub('\u2003\u2003', '\u2003', text)  # multiple whitespaces
    text = re.sub('\t\t', '\t', text)
    
    text = list_replace \
        ('\u02CC\u0307\u0323\u2022\u2023\u2043\u204C\u204D\u2219\u25E6\u00B7\u00D7\u22C5\u2219\u2062',
         '.', text)
    
    text = list_replace('\u2217', '\u002A', text)
    
    text = list_replace('…', '...', text)
    
    text = list_replace('\u2241\u224B\u2E2F\u0483', '\u223D', text)  # tilde sign
    
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
            (
            '\u20BD\u0024\u00A3\u20A4\u20AC\u20AA\u2133\u20BE\u00A2\u058F\u0BF9\u20BC\u20A1\u20A0\u20B4\u20A7\u20B0\u20BF\u20A3\u060B\u0E3F\u20A9\u20B4\u20B2\u0192\u20AB\u00A5\u20AD\u20A1\u20BA\u20A6\u20B1\uFDFC\u17DB\u20B9\u20A8\u20B5\u09F3\u20B8\u20AE\u0192')
    
    alphabet = list \
            (
            '\t\n\r абвгдеёзжийклмнопрстуфхцчшщьыъэюяАБВГДЕЁЗЖИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ,.[]{}()=+-−*&^%$#@!?~;:0123456789§/\|"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')
    
    alphabet.append("'")
    
    allowed = set(currencies + alphabet)
    
    cleaned_text = [sym for sym in text if sym in allowed]
    cleaned_text = ''.join(cleaned_text)
    
    return cleaned_text


def cleanhtml(raw_html):
    # get rid of fragmets of xml code
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext