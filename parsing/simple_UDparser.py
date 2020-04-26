'''
April 26, 2020
Given a folder of clean text data, get a folder with parsed texts in *.conllu format
No cleaning, tokenisation or filtering performed!

USAGE:
-- install pip install ufal.udpipe
-- choose and download a model for your language (description, inc. performance: http://ufal.mff.cuni.cz/udpipe/models#universal_dependencies_25_models)
-- go to parsing folder
-- run: python3 simple_UDparser.py --input en_media/ --output en_media_conllu --model english-ewt-ud-2.3-181115.udpipe
'''


import os, sys
from ufal.udpipe import Model, Pipeline
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', help="Path to prepared input files", required=True)
parser.add_argument('--output', help="Where you want the parsed texts", required=True)
parser.add_argument('--model', default='english-ewt-ud-2.3-181115.udpipe', help='Path to the lang model you want to use')
args = parser.parse_args()

start = time.time()

parse_out = args.output
os.makedirs(parse_out, exist_ok=True)

model = Model.load(args.model)
pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
print('UD model is loaded')

counter = 0
files = [f for f in os.listdir(args.input)]
for f in files:
    with open(args.input + f, 'r', errors='ignore') as input_text, open(args.output + f.replace('.txt', '.conllu'), 'w') as udout:
        try:
            text = input_text.read().strip()
        except UnicodeDecodeError:
            print('Unicode error in input file: %s; skipping it' % f)
            continue
        
        ud_tagged = pipeline.process(text)
        udout.write(ud_tagged)
                
        ### Monitor progress:
        if counter % 10 == 0:
            print('%s files processed' % counter, file=sys.stderr)

end = time.time()
processing_time = int(end - start)
print('Processing %s (%s files) took %.2f minites' % (args.input, counter, processing_time / 60), file=sys.stderr)
