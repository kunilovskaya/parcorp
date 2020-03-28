"""
this script produces stats for a select number of Universal dependencies from a folder of *.conllu files
adjust the dependencies you want to extract

If you want to use the output in ML experiment or statistic analysis, you might want to adjust the last folder names for each sybcorpus to represent a subcorpus,
i.e. a label in ML

USAGE: python3 stats/by_doc_analyze_treebank.py formats/mock_tq_corpus_lempos/good/conllu/ > stats/tables/ud_stats.tsv

"""

import sys, os
from collections import OrderedDict
import numpy as np

def relation_distribution(tree):
    sent_relations = [w[3] for w in tree]
    distribution = {relation: sent_relations.count(relation) for relation in relations}

    # Converting to probability distribution
    # 'probabilities' are basically ratio of the rel in question to all rels in the sentence
    total = sum(distribution.values())  # counts the number of all instances of all dependancies in the sent

    for key in distribution:
        try:
            distribution[key] /= total
        except ZeroDivisionError:
            distribution[key] = 0
    return distribution  # a dict rel : its ratio to all words int the sent

if __name__ == "__main__":
    many = sys.argv[1]
    folder = len(os.path.abspath(many).split('/')) - 1
    filtering = True  # Filter out punctuation and short sentences?
    min_length = 3

    if filtering:
        relations = OrderedDict(
            [('acl', []), ('acl:relcl', []), ('advcl', []), ('advmod', []), ('amod', []), ('appos', []),
             ('aux', []), ('aux:pass', []), ('case', []), ('cc', []), ('ccomp', []), ('compound', []),
             ('conj', []), ('cop', []), ('csubj', []), ('csubj:pass', []), ('det', []),
             ('discourse', []), ('fixed', []), ('flat', []),
             ('flat:foreign', []), ('flat:name', []), ('iobj', []), ('mark', []), ('nmod', []),
             ('nsubj', []), ('nsubj:pass', []), ('nummod', []), ('nummod:gov', []),
             ('obj', []), ('obl', []), ('orphan', []), ('parataxis', []), ('xcomp', []), ])
    else:
        relations = OrderedDict([('acl', []), ('acl:relcl', []), ('advcl', []), ('advmod', []), ('amod', []),
                                 ('appos', []), ('aux', []), ('aux:pass', []), ('case', []), ('cc', []), ('ccomp', []),
                                 ('clf', []), ('compound', []), ('conj', []), ('cop', []), ('csubj', []), ('dep', []),
                                 ('det', []), ('discourse', []), ('dislocated', []), ('expl', []), ('fixed', []),
                                 ('flat', []), ('flat:foreign', []), ('flat:name', []), ('goeswith', []), ('iobj', []),
                                 ('list', []), ('mark', []), ('nmod', []), ('nsubj', []), ('nsubj:pass', []),
                                 ('nummod', []),
                                 ('nummod:entity', []), ('nummod:gov', []), ('obj', []), ('obl', []), ('obl:agent', []),
                                 ('orphan', []), ('parataxis', []), ('punct', []), ('reparandum', []), ('root', []),
                                 ('vocative', []), ('xcomp', []), ])

    # add doc and corpus names to the output
    headers = ['doc', 'group']

    for rel in relations.keys():
        headers.append(rel)
    for i in headers:
        print(i, end="\t")
    print('\n')

    # Now let's start analyzing the treebank as a set of documents
    bank = [f for f in os.listdir(many) if f.endswith('.conllu')]

    for f in bank:
        # collect sentence-based counts
        words = open(many + f, 'r').readlines()
        sentences = []
        current_sentence = []
        for line in words:
            if line.strip() == '':
                if current_sentence:
                    sentences.append(current_sentence)
                current_sentence = []
                # if the number of sents can by devided by 1K without a remainder, print!
                if len(sentences) % 1000 == 0:
                    print('I have already read %s sentences' % len(sentences), file=sys.stderr)
                continue
            if line.strip().startswith('#'):
                continue
            res = line.strip().split('\t')
            (identifier, token, lemma, upos, xpos, feats, head, rel, misc1, misc2) = res
            if '.' in identifier:  # ignore empty nodes that are used in the enhanced representations
                continue
            # this is a list of data pieces from conllu that gets into [sentences]
            current_sentence.append((int(identifier), int(head), token,rel))

        if current_sentence:
            sentences.append(current_sentence)

        if filtering:
            sentences = [s for s in sentences if len(s) >= min_length]
        # collect treebank-based averaged stats
        # for each new file clear values from the dicts
        for value in relations.values():
            del value[:]

        for i in range(len(sentences)):
            sentence = sentences[i]
            
            rel_distribution = relation_distribution(sentence)
            for rel in relations.keys():
                relations[rel].append(rel_distribution[rel])
        '''
        count for all actually used sentences
        '''

        doc = os.path.splitext(os.path.basename(many + f))[0]  # without extention
        cl = os.path.abspath(many).split('/')[folder] # this is where the name of the group is generated
        print(doc, cl, sep='\t', end='\t')

        allvalues = []

        for rel in relations.keys():
            data = np.average(relations[rel])  # pulls out lists of values and averages them for sents in this bank
            allvalues.append(str(data))
        print('\t'.join(allvalues))
