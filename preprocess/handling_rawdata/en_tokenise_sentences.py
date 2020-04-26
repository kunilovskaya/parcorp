'''
TASK:
produce one-sentence per-line format from clean texts
requires NLTK
USAGE: python3 en_tokenise_sentences.py --input /path/to/folder/ --output /where/you/want/it/split/
'''

from __future__ import division
import sys, os
import nltk.data
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', help="Path to a folder with raw txt files", required=True)
parser.add_argument('--output', help="Path to the folder where you want the files with tokenised sentences", required=True)

args = parser.parse_args()

infolder = args.input
outto = args.output
os.makedirs(outto, exist_ok=True)

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')  # adjust for other languages
abbrev = {'&Co', 'AUG', 'Adm', 'Ala', 'Ald', 'App.Cas', 'Ariz', 'Ark', 'Assn', 'Assoc', 'Att', 'Aug', 'Av', 'Ave',
             'Bancorp', 'Bde', 'Bhd', 'Blvd', 'Brig', 'Bros', 'C.-in-C', 'CO', 'CORP', 'COS', 'Ca', 'Calif',
             'Canada-U.S', 'Canadian-U.S', 'Capt', 'Cas', 'Ch', 'Ch.App', 'Ch.D', 'Cia', 'Cie', 'Cm', 'Cmd',
             'Cmnd', 'Co', 'Col', 'Colo', 'Conn', 'Corp', 'Cos', 'Cowp', 'Cr.App.R', 'Crim.L.R', 'D-Mass',
             'D.Litt', 'D.Phil', 'DFl', 'Dec', 'Del', 'Dep', 'Dept', 'Deut', 'Diod', 'Div', 'Dr', 'Drs', 'Dtr',
             'Durn', 'E.g', 'ESQ', 'Eph', 'Eq', 'Eqn', 'Eqns', 'Esq', 'Etc', 'Exch', 'Exod', 'Ext', 'FIG', 'Fam', 'Feb',
             'Fig', 'Figs', 'Fla', 'Ft', 'G.m.b.H', 'Ga', 'Gen', 'Gov', 'Hdt', 'Hon', 'INC', 'Ibid', 'Ill', 'Inc',
             'Ind', 'InfoCorp', 'Intercorp', 'Invest', 'JJ', 'JR', 'Jan', 'Japan-U.S', 'Jr', 'Jud', 'Kan', 'Korean-U.S',
             'Ky', 'L.JJ', 'L.R.Ir', 'LL.M', 'LTD', 'La', 'Lt', 'Lt.-Col', 'Ltd', 'Ltda', 'M.Ed', 'M.Litt', 'M.Phil',
             'Maj', 'Mass', 'Md', 'Me.T.A', 'Messrs', 'Mfg', 'Mich', 'Minn', 'Miss', 'Mo', 'Mod.Rep', 'Mont',
             'Mr', 'Mrs', 'Ms', 'Neb', 'Nev', 'No', 'Non-U.S', 'Nos', 'Nov', 'Oct', 'Oe', 'Okla', 'Ont', 'Op',
             'Ore', 'P.o.s', 'Pa', 'Ph', 'Ph.D', 'Pp', 'Prev', 'Prof', 'Prop', 'Pte', 'Ptr', 'Pty', 'Reg', 'Regt',
             'Rep', 'Reps', 'Repub', 'Ret', 'Rev', 'Rom', 'S.p.A', 'Sec', 'Sen', 'Sens', 'Sept', 'Sgt', 'Sh.Ct',
             'Sino-U.S', 'Soc', 'Som', 'Soviet-U.S', 'Sp', 'Sr', 'St', 'Ste', 'Suff', 'Syll', 'T.B.G.A.S', 'Tenn',
             'Tex', 'Thess', 'Thuc', 'Transp', 'Trop', 'U.S.-U.K', 'U.S.-U.S.S.R', 'U.S.P.G.A', 'Univ', 'V.-C', 'Va',
             'Vict', 'Vol', 'Vt', 'W.Va', 'Wash', 'Wis', 'Wyo', 'a-Ex-dividend', 'a.c', 'a.g.m', 'a.k.a', 'a.m', 'al',
             'anti-U.S', 'approx', 'b.s', 'bldg', 'c.c', 'c.c.d', 'c.e.o', 'c.f', 'c.g', 'c.v', 'c/s', 'cap', 'cf', 'ch',
             'cit', 'clar', 'co', 'col', 'cols', 'constr', 'cp', 'cwt', 'd.c', 'd.f', 'd.i.l', 'd.p.c', 'def', 'dw',
             'e-Estimated', 'e.g', 'e.m.f', 'e.p.s.p', 'edn', 'edns', 'est', 'etc', 'ex-L.C.C', 'fig', 'fl',
             'fol', 'ft', 'gen', 'govt', 'h.p', 'hon', 'hrs', 'i.c', 'i.e', 'ibid', 'inc', 'incl', 'juv', 'k.p.h',
             'l.e.d', 'lbs', 'loc', 'm.d', 'm.p.h', 'msec', 'n.d', 'n.m.r', 'non-U.K', 'non-U.S', 'norw', 'nos', 'oz',
             'ozs', 'p', 'p.a', 'p.c', 'p.m', 'p.o.s', 'p.p.m', 'p.s.i', 'p.w', 'pl', 'pls', 'pos', 'pp', 'pres',
             'president-U.S', 'pro-U.S', 'q.v', 'qq.v', 'r.f', 'r.h', 'r.m.s', 'r.m.s.d', 'r.p.m', 'r.s.s', 'ref',
             's', 's.a', 's.a.e', 's.d', 's.e.m', 's.r.l', 's.t.p', 'spp', 'sq.ft', 'sq.m', 'subss', 'v', 'v.B', 'v.w',
             'var', 'viz', 'vol', 'vols', 'vs', 'w.c', 'ca', 'sic', 'p', 'P', 'ex', 'cf', 'Mt'}

sentence_tokenizer._params.abbrev_types.update(abbrev)
print("hello! sentence tokenisation in progress")


def sentence_splitter(text):
    return sentence_tokenizer.sentences_from_text(text.strip(), realign_boundaries=True)


files = [f for f in os.listdir(infolder) if f.endswith('.txt')]  # adjust file extension appropriately!
num_files = 0
for f in files:
    num_files += 1
    print(f)
    text = open(infolder + f, 'r').readlines()
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
print("%d files successfully split and written to the original folder with the different extention (*.split)" % num_files)
