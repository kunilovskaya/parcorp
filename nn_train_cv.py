#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# March 11, 2019: M.Kunilovskaya experiments based on:
# Copyright (C) 2018  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# Inspired by https://www.depends-on-the-definition.com/classify-toxic-comments-on-wikipedia

# how to run:
## activate the environment with GPU tensorflow installation
## set the mode (crossv, res); language is deduced from filenames; type of representation (mixed, lex) is required as an kwarg -r
# if crossv = 1
## python3 nn_train_cv.py -1 nn_train_input/en_cc300raw.vec.gz -i nn_train_input/en2211.ol -a nn_train_input/en2211.ann -d nn_train_input/en.brieftag.num -f 1500 -k 10 -r mixed
## if learning from lemmatized, no stopwords input:
## python3 nn_train_cv.py -1 nn_train_input/en_wiki300lem_stop.vec.gz -i nn_train_input/en1624_nf.ol -a nn_train_input/en1624.ann -d nn_train_input/en.brieftag.num -f 65000 -k 10 -r lex

import time
starttime=int(time.time())

import sys, re
import pandas as pd
import numpy as np
import smallutils as ut

import argparse


from keras.preprocessing import sequence
from keras.models import Model, Input
from keras.layers import Dense, Embedding, GlobalMaxPooling1D, SpatialDropout1D, Conv1D, MaxPooling1D, LSTM, Bidirectional, Dropout, concatenate, InputSpec
from keras import losses
from keras.optimizers import Adam

from keras.engine.topology import Layer
from keras import initializers as initializers
from keras import backend as K
from skmultilearn.model_selection import IterativeStratification
from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit

parser = argparse.ArgumentParser(description="A Keras Model for Genre Classification")
parser.add_argument('--mname', type=str, default='bilstma', help='Model type')
parser.add_argument('-1', '--embeddings', type=str, help='source embeddings')
parser.add_argument('-i', '--inputfile', type=str, help='one-doc-per-line training corpus')
parser.add_argument('-a', '--annotations', type=str, help='tab-separated FTDs with the header and text ids')
parser.add_argument('-d', '--dictionary', type=str, help='frequencies and POS annotations')
parser.add_argument('-r', '--representation', type=str, help='lemmatized or raw input')
parser.add_argument('-f', '--frqlimit', type=int, default=1500, help='how many words left with their forms')
parser.add_argument('-x', '--maxlen', type=int, default=1000, help='to shorten docs')
parser.add_argument('-w', '--wordlist', type=str, help='extra words to add to the lexicon')
parser.add_argument('-l', '--loss', type=str, default='binary_crossentropy', help='loss for training from keras')
# parser.add_argument('-l', '--loss', type=str, default='mean_squared_error', help='loss for training from keras')
parser.add_argument('-m', '--metrics', type=str, default='mae', help='metrics from keras')
parser.add_argument('-b', '--batch_size', type=int, default=32)
parser.add_argument('-e', '--epochs', type=int, default=10)
parser.add_argument( '--dropout', type=float, default=0.2)
parser.add_argument( '--valsplit', type=float, default=0.1)
parser.add_argument('-s', '--seed', type=int, default=42)
parser.add_argument('-k', '--topk', type=int, default=10, help='number of predicted labels to output')
parser.add_argument('--device', type=str, default='gpu', help='Choose the device. Options: cpu, gpu')

class AttentionWeightedAverage(Layer):
	"""
	Computes a weighted average attention mechanism from:
		Zhou, Peng, Wei Shi, Jun Tian, Zhenyu Qi, Bingchen Li, Hongwei Hao and Bo Xu.
		“Attention-Based Bidirectional Long Short-Term Memory Networks for Relation Classification.”
		ACL (2016). http://www.aclweb.org/anthology/P16-2034
	How to use:
	see: [BLOGPOST]
	"""
	
	def __init__(self, return_attention=False, **kwargs):
		self.init = initializers.get('uniform')
		self.supports_masking = True
		self.return_attention = return_attention
		super(AttentionWeightedAverage, self).__init__(**kwargs)
	
	def build(self, input_shape):
		self.input_spec = [InputSpec(ndim=3)]
		assert len(input_shape) == 3
		
		self.w = self.add_weight(shape=(input_shape[2], 1),
		                         name='{}_w'.format(self.name),
		                         initializer=self.init)
		self.trainable_weights = [self.w]
		super(AttentionWeightedAverage, self).build(input_shape)
	
	def call(self, h, mask=None):
		h_shape = K.shape(h)
		d_w, T = h_shape[0], h_shape[1]
		
		logits = K.dot(h, self.w)  # w^T h
		logits = K.reshape(logits, (d_w, T))
		alpha = K.exp(logits - K.max(logits, axis=-1, keepdims=True))  # exp
		
		# masked timesteps have zero weight
		if mask is not None:
			mask = K.cast(mask, K.floatx())
			alpha = alpha * mask
		alpha = alpha / K.sum(alpha, axis=1, keepdims=True)  # softmax
		r = K.sum(h * K.expand_dims(alpha), axis=1)  # r = h*alpha^T
		h_star = K.tanh(r)  # h^* = tanh(r)
		if self.return_attention:
			return [h_star, alpha]
		return h_star
	
	def get_output_shape_for(self, input_shape):
		return self.compute_output_shape(input_shape)
	
	def compute_output_shape(self, input_shape):
		output_len = input_shape[2]
		if self.return_attention:
			return [(input_shape[0], output_len), (input_shape[0], input_shape[1])]
		return (input_shape[0], output_len)
	
	def compute_mask(self, input, input_mask=None):
		if isinstance(input_mask, list):
			return [None] * len(input_mask)
		else:
			return None


def createmodel(mname='FT'):
	# The arg indicates that the expected input will be batches of N-dimensional vectors (words perdoc)
	inp = Input(shape=(args.maxlen,))  # used to instantiate a Keras tensor.
	
	# Turns positive integers (indexes) into dense vectors of fixed size (default batch_size = 64).
	# sp.shape[0] = No of rows in embeddings/vectors = no of words in the voc (?), sp.shape[1] = vector length
	print('Input to the Embedding layer', sp.shape[0], sp.shape[1])
	x = Embedding(sp.shape[0], sp.shape[1], weights=[sp], trainable=True)(inp)
	print("Output of the Embedding layer", x.shape)
	print('Running ' + mname, file=sys.stderr)
	if mname == 'CNN':
		x = Conv1D(256, 5, activation='sigmoid')(x)
		x = MaxPooling1D(5)(x)
		x = SpatialDropout1D(args.dropout)(x)
		x = Conv1D(128, 5, activation='sigmoid')(x)
		x = MaxPooling1D(5)(x)
		x = Conv1D(64, 5, activation='sigmoid')(x)
		x = GlobalMaxPooling1D()(x)
	elif mname == 'bilstm':
		x = Bidirectional(LSTM(100))(x)
	elif mname == 'bilstma':  # bilstm with attention, see https://github.com/tsterbak/keras_attention
		d = 0.5
		rd = 0.5
		# helps to get rid of strongly correlated feature maps, which decrease effective learning rate
		x = SpatialDropout1D(0.5)(x)
		x = Bidirectional(LSTM(units=128, return_sequences=True, dropout=d,
		                            recurrent_dropout=rd))(x)
		x, attn = AttentionWeightedAverage(return_attention=True)(x)
	else:
		# pooling layer,which combine the outputs of neuron clusters at one layer into a single neuron in the next layer.
		# Unlike fully connected layers which connect every neuron in one layer to every neuron in another layer, this function uses the maximum value from each of a cluster of neurons at the prior layer.
		x = GlobalMaxPooling1D()(x)  # a simple imitation of fasttext
	# Dropout consists in randomly setting a fraction rate of input units to 0 at each update during training time, which helps prevent overfitting.
	x = Dropout(args.dropout)(x)
	# map all inputs into the range of 0 to 1
	output = Dense(y_train.shape[1], activation='sigmoid')(x)
	model = Model(inputs=inp, outputs=output)
	model.compile(loss=args.loss,
	              # binary_crossentropy to output to model the output as a independent bernoulli distributions per label
	              optimizer=Adam(0.01),
	              metrics=[args.metrics])  # cosine and mae (=Mean Absolute error) because our output is a vector
	print('Model configuration', model.get_config())
	print('Model summary', model.summary())
	return (model)


if __name__ == '__main__':
	
	import tensorflow as tf
	import os
	
	outname=re.sub(' ','=','_'.join(sys.argv))
	outname=re.sub('/','@',outname)
	
	args = parser.parse_args()
	
	if args.device == 'cpu':
		## select the number of CPU workers=threads to be used
		config = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=4,
										  inter_op_parallelism_threads=4,
										  allow_soft_placement=True)  # ,device_count = {'CPU' : 2, 'GPU' : 1}
		os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
	if args.device == 'gpu':
		config = tf.compat.v1.ConfigProto()
		# os.environ["CUDA_VISIBLE_DEVICES"]="0,1"
		print('=== DEFAULT availability', K.tensorflow_backend._get_available_gpus())
		# sess = tf.Session(config=config)
		## select what you want to run it on
		# config = tf.ConfigProto(device_count={'GPU': 0, 'CPU': 4})
		# config.gpu_options.visible_device_list = '1'  # only see the gpu 1
		config.gpu_options.visible_device_list = '0,1'  # see the gpu 0, 1, 2
		
		## replace: tf.ConfigProto by tf.compat.v1.ConfigProto
		print("====== Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
		
		tf.compat.v1.logging.set_verbosity(tf.logging.INFO)
	
	np.random.seed(args.seed)
	print('Parameter list: %s' % outname, file=sys.stderr)
	
	if 'en' in args.annotations:
		lang = 'en'
	if 'ru' in args.annotations:
		lang = 'ru'
	else:
		print('I do not see the language indication in the name of the annotations file!')
	
	reps = args.representation # 'mixed', 'lex'
	
	#do you want crossvalidation (or train-test)?
	crossv = 1
	# set the desired output format
	res = 1
	
	# models_maps_to = lang+'_h5/cv_res/'
	# os.makedirs(models_maps_to, exist_ok=True)
	
	res_to = lang+'_nn_res/cv_res/'
	os.makedirs(res_to, exist_ok=True)
	
	# this is the exact order of the y in the model training setting
	ann_order = ['A1', 'A4', 'A7', 'A8', 'A9', 'A11', 'A12', 'A14', 'A16', 'A17']
	mapping = {'A1': 'argument', 'A16': 'info', 'A8': 'news', 'A11': 'personal', 'A17': 'eval', 'A12': 'promotion',
	           'A14': 'scitech', 'A9': 'legal', 'A7': 'instruction', 'A4': 'fiction'}
	config = tf.ConfigProto()
	jit_level = tf.OptimizerOptions.ON_1
	config.graph_options.optimizer_options.global_jit_level = jit_level
	
	sess = tf.Session(config=config)
	tf.keras.backend.set_session(sess)
	
	with open(args.inputfile) as f:
		if reps == 'mixed':
			dictlist,frqlist=ut.readfrqdict(args.dictionary,args.frqlimit)
			X_train=[ut.mixedstr(l,dictlist,frqlist) for l in f] # list of lists
			print("===Lets get a 100th doc===", X_train[-10:-1])
			print(len(X_train))
		if reps == 'lex': #
			X_train=[]
			for l in f:
				l=[w for w in l.split()]
				X_train.append(l) # list of lists
			
	print(X_train[1], file=sys.stderr)
	print('Train samples from %s' % args.inputfile, file=sys.stderr)

	y_train = pd.read_csv(args.annotations,header=0,index_col=0,sep='\t')
	y_train = y_train / 2  #[0..2] annotations need to match the sigmoid function
	print('Train data: %d train, %d labels' % (len(X_train), len(y_train)), file=sys.stderr)
	
	wlist=set([w for doc in X_train for w in doc])

	print('Lex size: %d' % len(wlist), file=sys.stderr)
	print('!!!THIS SET IS NOT WEIRD ANYMORE!!!', list(wlist)[0:1700])

	sp,w2i = ut.read_embeddings(args.embeddings,vocab=wlist)
	
	
	print('Read %d embeddings in %d dimensions' % (sp.shape[0], sp.shape[1]), file=sys.stderr)
	
	x_train=[]
	for doc in X_train:
		x_train.append([w2i[w] for w in doc]) # that's where words in texts are replaced with indices corresponding to the order of wds in embeddings (=sp)
	if not sp.shape[0]==len(w2i):
		print('!!ERROR: Old lex size: %d, new %d. Offending words' % (sp.shape[0], len(w2i)), file=sys.stderr)
		for w in w2i:
			if sp.shape[0]<=w2i[w]:
				print(w, file=sys.stderr)
	print('===Average train doc length: %d' % np.mean(list(map(len, x_train)), dtype=int), file=sys.stderr)

	x_train = sequence.pad_sequences(x_train, maxlen=args.maxlen)
	loadtime=int(time.time())

	print('Load time: %d min' % ((loadtime-starttime)/60), file=sys.stderr)

	print('Building a model on the 0.8 train with keyworded validation of 0.1', file=sys.stderr)
	# k_fold = IterativeStratification(n_splits=2, order=1)
	# direct stratification is problematic with 10-dim vector to predict
	kf_counter = -1
	if crossv:
		n = 10
	else:
		n = 1
	msss = MultilabelStratifiedShuffleSplit(n_splits=n, test_size=0.2, random_state=100)
	for train_index, test_index in msss.split(x_train, y_train):
		kf_counter += 1
		fold = 'fold' + str(kf_counter)
		print(fold)

		X_train, X_test = x_train[train_index], x_train[test_index]
		yy_train, y_test = y_train.iloc[train_index], y_train.iloc[test_index]
		files = y_test.index.tolist()

	# multiply all numeric values in the y_test df (which has a useful 'ID' column!) by two to get a slice of original annotation format

		testset_ann = y_test.select_dtypes(exclude=['object']) * 2
		print('Writing annotations slice for the %s:' % fold,
		      len(y_test), file=sys.stderr)
		testset_ann.to_csv(res_to+'%s_%s%s_%s.ann' % (lang, reps, len(X_train),fold), sep='\t')

			
		K.clear_session()
		model = createmodel(args.mname)
		# A label vector should look like l = [0,0,1,0,1]
		# if classes 3 and 5 are present for the label ('multi-hot-encoding')
		
		model.fit(X_train, yy_train, batch_size=args.batch_size, epochs=args.epochs,
		          validation_split=args.valsplit)
	
		predict_t = model.predict(X_test, batch_size=args.batch_size)
		
		## this is required by the compare_model.ipynb for evaluation on real, rather than binarized values
		preds_nested = []
		print('Writing predictions (.res format) on %s:' % fold, len(predict_t))
		for fscores in predict_t:
			preds_nested.append(fscores.tolist())
		print(len(preds_nested))

		df = pd.DataFrame(preds_nested).round(6)
		df.columns = [mapping[ann_order[x]] + ann_order[x] for x in range(len(ann_order))]
		df.insert(0, 'filename', files)

		# print(df.head())

		df.to_csv(res_to+'%s_%s_%sbiLSTMa_%s.res'% (lang, reps, len(X_train), fold), index=False, sep='\t')  # 10ep1624
		print('The %s has %s texts' % (fold, len(predict_t)), file=sys.stderr)

		print('Writing predictions (.pred format for evaluation) on %s:' % fold, len(predict_t), file=sys.stderr)
		
		with open(res_to+'%s_%s%s_%s_biLSTMa.pred'% (lang, reps, len(X_train), fold), "w") as outf:
			'''
			this is a support output used for evaluation only
			'''
			for fscores in predict_t:
				outstr = ['__label__%s %.5f' % (y_train.columns[i], fscores[i]) for i in np.argsort(-fscores)[:args.topk]]
				print('\t'.join(outstr), file=outf)
		print('The %s has %s texts' % (fold, len(predict_t)), file=sys.stderr)
			
		traintime=int(time.time())
		
		print('Train time: %d min' % ((traintime-loadtime)/60), file=sys.stderr)
		
		### I don't need the models for each fold for evaluation. For producing actual working models see a separate script
		
		# model_filename = models_maps_to+'%s%s_%s_biLSTMa_%s.h5' % (lang, len(X_train), reps, fold)
		#
		# pickle.dump(w2i, open('%s.map' % (model_filename), 'wb'))
		# print('Mappings of words to representations in the model are saved to %s.map' % model_filename, file=sys.stderr)
		# model.save(model_filename)
		# print('Model saved to', model_filename, file=sys.stderr)
	
