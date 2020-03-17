# coding: utf-8

# all compare functions

import pandas as pd
import numpy as np
from scipy.spatial import distance
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
from statistics import mean
import scipy.spatial as sp

import pandas as pd
import os, sys, re
from collections import OrderedDict
from collections import defaultdict
from operator import itemgetter



def load_bibs(path):
    bib = pd.read_csv(path, index_col='Filename', sep='\t')
    bib.drop(['CORPUS'], axis=0, inplace=True)
    bib.drop(['Tokens', 'Unnamed: 69'], axis=1, inplace=True)
    print(bib.shape)
    
    #     print('My data to predict:', bib.head())
    
    return bib

def my_open(path):
    if path.endswith('.csv') or path.endswith('.ann'):
        data = pd.read_csv(path, sep='\t')
    
    elif path.endswith('.txt'):
        data = open(path, 'r').readlines()
    
    elif path.endswith('.pred'):
        data = pd.read_csv(path, sep='\t')
    
    elif path.endswith('.res'):
        data = pd.read_csv(path, index_col='filename', sep='\t').sort_index()
        
    elif path.endswith('.dat'):
        # print('Are you sure it is the table from MAT? If not, open manually')
        data = load_bibs(path)
    # assume it is a folder and return a fh
    else:
        print('Make sure you have chosen the sound method of opening this file')
        data = [f for f in os.listdir(path)]  # if f.endswith('.nf')]
    
    return data

def preprocess_anns(annfn, name): # NN, ML
    ann = pd.read_csv(annfn, index_col='ID', sep='\t').sort_index()
    # bring the default anno in compliance with what NN got
    if name == 'NN':
        annos = ann/2
    
    elif name == 'ML':
    # bring the default anno in compliance with what ML got
    # replace 0, 0.5 with 0 and 1, 2 with 1 
        annos = pd.DataFrame(np.where(ann >= 0.5, 1, 0))
        annos.columns = ann.columns

        # adjust the file extensions that are not all in place in annotations, but have to be there when we got separate files for MAT annotation
        new_idx = []
        for i in ann.index.tolist():
            if i.endswith('.txt'):
                i = i[:-4]
            else:
                i=i
            new_idx.append(i)
        print(len(new_idx))

        annos['filename'] = new_idx #adding the fns from the original df; it is sorted!
        annos.set_index('filename', inplace=True)
        annos.name = 'humans'
        
    return annos

# this function returns comparative analysis results for NN and ML(RandomForest) performance
# based on *.res returned by my respective NN/ML_predict scripts
# get real-value preds for each FTD from two models into one df

# merge two dfs while inserting a corpus column from df.names
def merge_them(df1, df2):
    df11 = df1.copy()
    df22 = df2.copy()
    
    df11.insert(0, 'corpus', df1.name)
    df22.insert(0, 'corpus', df2.name)
    
    all_preds = df11.append(df22)
    
    return all_preds

def compare_models(df_a, df_b, verbose=0):
    # concatenate dfs after renaming cols in the first one

    df_a0 = df_a.rename(columns=lambda x: x + '_0')
    # df_a0 = df_a.copy()
    both = pd.concat([df_a0, df_b], axis=1)
    # print(both.head())
    # lets see how correlated are mixed and lemmatized outputs are
    # (A) FTD-wise
    # Covariance indicates the level to which two variables vary together.
    # np.corrcoef returns the normalised covariance matrix = Pearson product-moment correlation coefficients
    # the function returns a matrix, we are interested in only one value in it, therefore slicing
    df_a_cols = both.columns[:10]
    df_b_cols = both.columns[10:]
    mean_cor = []
    
    if verbose:
        print("Pearson product-moment correlation coefficients for 10 FTD predictions for %s texts in input:" % len(both))
    
    for (x, y) in zip(df_a_cols, df_b_cols):
        if verbose:
            print(x, '\t', np.corrcoef(both[x].values, both[y].values)[0, 1])
        mean_cor.append(np.corrcoef(both[x].values, both[y].values)[0, 1])
        # component-wise similarities
    if verbose:
        print('Correlation averaged over 10 FTDs: %.3f' % np.average(mean_cor))
    
    # scatter plot is not insightfull and does not do justice to the high corr coef;
    
    # but helps to see that predictions on lemmatized reps are more often around zero
    #     plt.figure(figsize=(7, 8))
    #     for col in df_a_cols:
    #         if 'A12' in col:
    #             plt.scatter(df_a0[col], df_b[col], s=None, c='b', marker=None, norm=None, vmin=None,
    #                      vmax=None, alpha=None, linewidths=None, verts=None,
    #                      edgecolors=None)
    #             plt.xlabel(df_a.name)
    #             plt.ylabel(df_b.name)
    #             plt.title('Correlation of real values predicted for FTDs by NNs on different reps')
    #             # plt.legend(lines, labels, loc=(0, -.38), prop=dict(size=11), ncol=2)
    #             plt.show()
    # (B) Samples-wise
    # grab 10 values for each text
    corrs = []
    for i in range(len(both)):
        
        co = np.corrcoef(both.iloc[i, :10].values, both.iloc[i, 10:].values)[0, 1]
        
        if not np.isnan(co):
            corrs.append(co)
        else:
            corrs.append(0)
            # print('===Gotcha None!', both.iloc[[i]])  # __idx__1986__id__1468-crmnewsdaily all zeros are predicted by nn
    if len(both[both.isin([np.nan]).any(1)]) != 0:
        print('Dataframe construction alert: something went wrong with matching indices of the input dfs!')
    else:
        print('Congrats! Dataframe constuction sanity check passed!!')
    if verbose:
        print('Average row-wise correlation:', mean(corrs))  # WHY THIS RETURNS nan??? because there are nans
    
    corr_stats = pd.DataFrame(corrs, columns=['corr'])
    corr_stats.insert(0, 'filename', both.index)
    # print(corr_stats.head())
    if verbose:
        print('Statistics on the row-wise correlations of 10 predicted values for each text')
        # print(corr_stats.describe())
    
    # get all rows on condition (corr >= 0.7) in one of the columns
    best_correlated = corr_stats.loc[corr_stats['corr'] >= 0.7]
    if verbose:
        print('Number of files on which the Pearson correlation for vals of two vectors is >= 0.7:',
          best_correlated.shape[0])
    #     print('Examples:\n', best_correlated.head())

    corrs0 = []
    # get me the offensive rows
    # print(both[both.isin([np.nan, np.inf, -np.inf]).any(1)])
    
    # print(both.head())
    for i in range(len(both)):
        both.fillna(0)
        sim = (1 - distance.euclidean(both.iloc[i, :10].values, both.iloc[i, 10:].values))
        corrs0.append(sim)
    #         corrs0.append(1 - distance.cosine(both.iloc[i,:10].values, both.iloc[i,10:].values))
    corr_stats0 = pd.DataFrame(corrs0, columns=['sim'])
    
    corr_stats0.insert(0, 'filename', both.index)
    # print('EMPTY??',both.head())
    if verbose:
        print()
        print('Averaged euclidean similarity for text vectors (half-rows):', corr_stats0['sim'].mean().round(3))
    
    best_correlated0 = corr_stats0.loc[corr_stats0['sim'] >= 0.7]
    if verbose:
        print('Number of files for which euclidean similarity for their vectors is >= 0.7:', best_correlated0.shape[0])
        print()
    return both

# zero out, round and lose occasional .txt extations in annotations
def zero_out(data):
    data0 = data.copy()
    # zero out values less than 0.1 but this returns an array
    # merged = pd.DataFrame(np.where(merged < 0.1, 0, merged))
    
    # the share brackets have a boolean mask passed to the assign operation
    data0[data0 < 0.1] = 0
    data0 = data0.apply(lambda x: round(x, 2))
    # lose fucking extensions!
    new_idx = data0.index.str.replace('.txt', '', regex=False)
    data0.index = new_idx
    
    return data0


# get best labels for each text from *.res

# name = NNm, NNlex ML
def get_dominants(df, name, corpus):  # accepts a df with fns as index and 10 cols of predicted vals
    
    unpredicted = 0
    confid_thresh = 0.2
    diehards = []
    
    polyfunc = 0
    poly_thresh = 0.7  # the smaller the thresh the bigger the diff
    bi_func = []
    
    # collect results on top predicted labels (one or two depending on how far they are apart):
    res = []
    if 'biLSTM' in name or 'NN' in name:
        for i in range(len(df)):
            # make a series of each row
            row_res = []
            row_df = df.iloc[i, :]
            
            # test the certainty threshold for the top prediction is met, if not return zeros
            if row_df.nlargest(2)[0] < confid_thresh:
                row_res = [df.index[i], 'None', 'None']
                res.append(row_res)
                unpredicted += 1
                diehards.append(df.index[i])
            
            # test if the predictions for two FTDs for one text are close to each other (and are above the thres!)
            elif row_df.nlargest(2)[1] / row_df.nlargest(2)[0] >= poly_thresh:
                row_res = [df.index[i], row_df.nlargest(2).index[0], row_df.nlargest(2).index[1]]
                res.append(row_res)
                polyfunc += 1
                bi_func.append(df.index[i])
            # don't forget those rows with one label
            else:
                row_res = [df.index[i], row_df.idxmax(axis=1),
                           'None']  # this row_df.nlargest()[0] gets the respective value
                res.append(row_res)
        # convert the list of lists to df
        predicted = pd.DataFrame(res, columns=['File', '%s_FTD1' % name, '%s_FTD2' % name])
        predicted.set_index('File', inplace=True)
    # do the same for ML scenario, only allow for at least three labels predicted with some certainty
    if 'Forests' in name or 'ML' in name:
        for i in range(len(df)):
            row_res = []
            row_df = df.iloc[i, :]
            if row_df.nlargest(2)[0] < confid_thresh:
                row_res = [df.index[i], 'None', 'None', 'None']
                res.append(row_res)
                unpredicted += 1
                diehards.append(df.index[i])
            elif row_df.nlargest()[1] / row_df.nlargest()[0] >= poly_thresh and row_df.nlargest()[2] / \
                    row_df.nlargest()[1] >= poly_thresh:
                row_res = [df.index[i], row_df.nlargest().index[0], row_df.nlargest().index[1],
                           row_df.nlargest().index[2]]
                res.append(row_res)
                polyfunc += 1
                bi_func.append(df.index[i])
            elif row_df.nlargest()[1] / row_df.nlargest()[0] >= poly_thresh:
                row_res = [df.index[i], row_df.nlargest().index[0], row_df.nlargest().index[1], 'None']
                res.append(row_res)
                polyfunc += 1
                bi_func.append(df.index[i])
            else:
                row_res = [df.index[i], row_df.idxmax(axis=1), 'None',
                           'None']  # this row_df.nlargest()[0] gets the respective value
                res.append(row_res)
        
        # convert the list of lists to df
        predicted = pd.DataFrame(res, columns=['File', '%s_FTD1' % name, '%s_FTD2' % name, '%s_FTD3' % name])
        predicted.set_index('File', inplace=True)
    
    print()
    print('Number of texts in %s with failed functional predictions at %s model (%s) confidence threshold:' % (
        corpus.upper(), confid_thresh, name), unpredicted)
    print('%s functional die-hards %r' % (name, diehards[:5]))
    
    print()
    print('Number of %s-predicted bi-functional texts at %s ratio of top two values:' % (name, poly_thresh), polyfunc)
    print('%s bi-functionals %r' % (name, bi_func[:5]))
    print('Max number of strong predictions per text:', predicted.shape[1] - 1)
    
    predicted.name = name
    return predicted  # this returns a df with best labels for each text


def get_crosscorp_dominants(df, corpus):  # accepts a df with fns as index and 10 cols of predicted vals
    
    unpredicted = 0
    confid_thresh = 0.2
    diehards = []
    
    polyfunc = 0
    poly_thresh = 0.7  # the smaller the thresh the bigger the diff
    bi_func = []
    
    # collect results on top predicted labels (one or up to three depending on how far they are apart):
    res = []
    for i in range(len(df)):
        # make a series of each row
        row_res = []
        row_df = df.iloc[i, :]
        
        # test the certainty threshold for the top prediction is met, if not return zeros
        if row_df.nlargest()[0] < confid_thresh:
            row_res = [df.index[i], 'None', 'None', 'None']
            res.append(row_res)
            unpredicted += 1
            diehards.append(df.index[i])
        # test if the predictions for two FTDs for one text are close to each other (and are above the thres!)
        elif row_df.nlargest()[1] / row_df.nlargest()[0] >= poly_thresh:
            row_res = [df.index[i], row_df.nlargest().index[0], row_df.nlargest().index[1]]
            res.append(row_res)
            polyfunc += 1
            bi_func.append(df.index[i])
        elif row_df.nlargest()[2] / row_df.nlargest()[1] >= poly_thresh:
            row_res = [df.index[i], row_df.nlargest().index[0], row_df.nlargest().index[1], row_df.nlargest().index[2]]
            res.append(row_res)
            polyfunc += 1
            bi_func.append(df.index[i])
        # don't forget those rows with one label
        else:
            row_res = [df.index[i], row_df.idxmax(axis=1),
                       'None']  # this row_df.nlargest()[0] gets the respective value
            res.append(row_res)
    
    # convert the list of lists to df
    # print(res)
    predicted = pd.DataFrame(res, columns=['File', 'FTD1', 'FTD2', 'FTD3'])
    predicted.set_index('File', inplace=True)
    
    print()
    print('Number of texts in %s with failed functional predictions at %s confidence threshold:' % (
    corpus.upper(), confid_thresh), unpredicted)
    print('%s functional die-hards %r' % (corpus, diehards[:5]))
    
    print()
    print('Number of %s-predicted bi-functional texts at %s ratio of top two values:' % (corpus, poly_thresh), polyfunc)
    print('%s bi-functionals %r' % (corpus, bi_func[:5]))
    
    predicted.name = corpus
    return predicted  # this returns a df with best labels for each text


# get fns for dominant functions to see whether these bars contain the same texts
def get_genre_fns(df):
    cols = df.columns.tolist()
    
    genres_nums = defaultdict(int)
    keys = 'argument fiction instruction news legal personal promotion scitech info eval else'.split()
    tuples = zip(cols, keys)  # the right order of TFDs!
    genres_fns = {k: [] for k in keys}
    genres_proba = {k: [] for k in keys}
    for col, key in tuples:
        #         print(type(df[col].values.tolist()))
        genres_proba[key].append(df[col].values)
    
    for i in df.index:
        eachrow = df.loc[i].sort_values(ascending=False)
        val = eachrow.max()
        idx = eachrow.idxmax()
        
        if val > 0.2:
            for key in keys:
                if key in idx:
                    genres_nums[key] += 1
                    genres_fns[key].append(i)
        else:
            genres_nums['else'] += 1
            genres_fns['else'].append(i)
    # print(genres_nums['else'])
    # outheader = ['FTD', 'mean_val', 'median', 'std', 'max', 'min']
    # print('\t'.join(outheader))
    
    # for k, v in genres_proba.items():
    #     if v:
    #         v = [i.round(3) for i in v]
    #         print('%s\t%s\t%s\t%s\t%s\t%s' % (k, np.average(v).round(3),
    #                                           np.median(v), np.std(v).round(3), np.max(v), np.min(v)))
    
    genres_nums_sort = OrderedDict(sorted(genres_nums.items(), key=itemgetter(1), reverse=True))
    tples = list(genres_nums_sort.items())
    # print(tples)
    print('Distribution of functional dominants in %s (percentage)' % df.name)
    for tu in tples:
        ratio = round(tu[1]/len(df)*100,0)
        print(' '.join(i for i in [tu[0], str(ratio)]), end="\n")
    return genres_fns


# get fns for dominant functions to see whether these bars contain the same texts
def intersections(fns_d1, fns_d2):
    collector = []
    for k in fns_d1.keys():
        #         print(k)
        top = np.max([len(fns_d1[k]), len(fns_d2[k])])
        #         print(top)
        #         if k == 'promotion':
        #          #find one-tail difference: fails in mixed but not in lex
        #             lostA12 = []
        #             for i in range(len(fns_d2[k])):
        #                 if fns_d1[k][i] not in fns_d2[k]:
        #                     lostA12.append(fns_d1[k][i])
        #                     print(fns_d1[k][i])
        
        #             print(len(lostA12))
        
        shared = set(fns_d1[k]).intersection(set(fns_d2[k]))
        ratio = len(shared) / top
        collector.append(ratio)
        on_average = (np.average(collector)).round(3)
        std = (np.std(collector)).round(3)
        
        print(k, np.round(ratio * 100, 1), '%', 'of max %s docs' % top)
    print()
    print('On average %5.2f (%5.2f)' % (on_average, std))
        
# this function can be used to compare different vectors for the same texts,
# so it will return a square matrix rather than 110X360 for texts from diff corpora
# can be fed dfs
def calc_sim(method, mat1, mat2, model):
    if method == 'cosine' or method == 'euclidean':
        sim_m = 1 - sp.distance.cdist(mat1, mat2, method)
#         print('Based on functional representations CroCO and RusLTC have the similarity score of %0.3f' % average_sim,
#               '(calculated as the averaged pair-wise %s similarity' % method, ')')
        df = pd.DataFrame(sim_m)
        df.index = mat1.index
        df.columns = mat2.index
        # print('WHY same files return diff value for max sim for k=7 and 8')
        # print(df)
        average_sim = np.nanmean(sim_m)
    if method == 'dot':
        sim_m = np.dot(mat1, mat2.T)
        average_sim = sim_m.mean()
    # print('Based on functional representations from %s the input corpora have the similarity score of %0.3f (calculated as the averaged pair-wise %s similarity)' % (model, average_sim, method))
    return sim_m, average_sim


def get_twins(sim, sim_measure, df1, df2, model):
    # FYI: axis=0 returns number of cols, axis=1 returns number of rows

    # this is an array of max similarity values (for ML they range from 0.931 to 0.997 for 64 most similar rltc texts)
    max_sim_vals = np.amax(sim, axis=1)
    print('The range of similarity values among most similar in %s output (%s):' % (model, sim_measure),
          round(np.sort(max_sim_vals)[0], 3), np.sort(max_sim_vals)[-1])
    
    print('======', max_sim_vals)
    
    # and these are rtlc indices of rtlc texts most similar to 110 croco as they appear in this matrix
    # YES, there are duplicates on the list
    corp2_twins_idx = np.argmax(sim, axis=1)
    
    # lets get fn pairs
    outstring = '_'.join(['twins', df1.name, df2.name, model])
    corp2_twins_fns = []
    my_dict = {'corpus1':[], 'corpus2':[]}
    
    with open('/home/masha/venv/genre-keras/res/' + outstring + '.tsv', 'w') as out:
        for i in range(len(sim)):
            corp2_twins_fns.append(df2.index[corp2_twins_idx[i]])
            out.write(df1.index[i]+'\t'+df2.index[corp2_twins_idx[i]]+'\n')
            print(df1.index[i] + '\t' + df2.index[corp2_twins_idx[i]])
            my_dict['corpus1'].append(df1.index[i])
            my_dict['corpus2'].append(df2.index[corp2_twins_idx[i]])
            
    #     print('Number of duplicates among most similar:')
    #     for k, v in dict(Counter(corp2_twins_fns)).items(): # convert to a regular dict
    #         if v > 1:
    #             print(k,'\t',v)
    print('Number of unique most similar texts from rltc:', len(set(corp2_twins_fns)))
    df = pd.DataFrame.from_dict(my_dict)
    return df, max_sim_vals

def get_labels_col(df):
    df_dominants = get_crosscorp_dominants(df, df.name)
    df_lab = df.copy()
    df_lab.insert(0, 'FTD1', df_dominants.FTD1.tolist())
    df_lab.insert(0, 'FTD2', df_dominants.FTD2.tolist())
#     df_lab.insert(0, 'FTD3', df_dominants.FTD3.tolist())
    df_lab.reset_index(inplace=True)
    labels = df_lab.apply(lambda x:'%s_%s' % (x['FTD1'],x['FTD2']),axis=1)

    new_col = 'labels'
    df_lab.insert(0, new_col, labels)

    df_lab.drop(['FTD1', 'FTD2'], axis=1, inplace=True)

    return df_lab

#feed a df and list of two top dominant functions and get a samples labeled variant
def labeled_samples(df):
    print(df.name)
    df_dominants = get_crosscorp_dominants(df, df.name)
    df_samples_lab = df.copy()
    df_samples_lab.insert(0, 'FTD1', df_dominants.FTD1.tolist())
#     df_lab.insert(0, 'FTD3', df_dominants.FTD3.tolist())
    df_samples_lab.reset_index(inplace=True)
    
    # print(df_samples_lab.head())

    labeled = df_samples_lab.apply(lambda x:'%s_%s' % (x['filename'],x['FTD1']), axis=1)
    # print(cro_nn_labeled.head())
    new_col = 'new_filename'
    df_samples_lab.insert(0, new_col, labeled)
    df_samples_lab.drop(['filename','FTD1'], axis=1, inplace=True)
    df_samples_lab.insert(0, 'FTD2', df_dominants.FTD2.tolist())
    labeled2 = df_samples_lab.apply(lambda x:'%s_%s' % (x[new_col],x['FTD2']),axis=1)
    # print(cro_nn_labeled.head())
    df_samples_lab[new_col] = labeled2
    df_samples_lab.drop(['FTD2'], axis=1, inplace=True)
    df_samples_lab.set_index('new_filename', inplace=True)
    print('Your samples are additionally labeled with dominants')
    return df_samples_lab

# get predicted labels for the most similar texts in both corpora --- do they coinside?
def show_labeled_twins(sim, df1, df2, model):
    max_sim_vals = np.amax(sim, axis=1)
    corp2_twins_idx = np.argmax(sim, axis=1)
    #     print('this is ok')
    outstring = '_'.join(['labeled_twins', df1.name, df2.name, model])
    corp2_twins_fns = []
    twins = {}
    counter = 0
    if 'NN' in df1.name or 'NN' in df2.name:
        df1.columns = ['FTD1', 'FTD2']
        df2.columns = ['FTD1', 'FTD2']
    else:
        pass

    with open('res/' + outstring + '.tsv', 'w') as out:
        for i in range(len(sim)):
            # lets get fn pairs
            twin1_fn = df1.index[i]
            twin2_fn = df2.index[corp2_twins_idx[i]]
            corp2_twins_fns.append(twin2_fn)

            twins[twin1_fn] = (df1.at[twin1_fn, 'FTD1'], df2.at[twin2_fn, 'FTD1'])
            #                 print(df2.at[twin2_fn, 'FTD1'])
            string = '\t'.join([twin1_fn, df1.at[twin1_fn, 'FTD1'], twin2_fn, df2.at[twin2_fn, 'FTD1']])
            out.write(string+'\n')
            # print(string)
        # print(twins)
        for k, v in twins.items():
            if v[0] == v[1]:
                counter += 1
            else:
                print(k, v[0], v[1])
    
    print('Number of texts returned as most similar (by %s) with coinsiding first FTDs of total %s:' % (model, len(sim)), counter)


# get me the filenames from each cluster aa well as associated predicted labels
import re
from collections import Counter
from collections import OrderedDict
import operator
import pickle


# this function expects that fns are_labeled_with top functions
def get_clustered_labels(clustered, corpus, filenames=True):
    
    clusters_dic = {}
    
    for i in clustered.index:
        print('====Cluster %s' % i)
        current_cluster_preds = []  #
        corps = []
        fns = []
        
        #cluster 9 [A04_argumentA1_None, A1A_argumentA1_None, A5Y..]
        # in bnc6cats scenario: A0D_fict_fictionA4_None
        
        labels = clustered.loc[i, ['files']].tolist()
        labels = [y.strip() for x in labels for y in x]
        # print(labels)
        for fn_lab in labels:
            bits = fn_lab.split('_')
            # print(bits)
            # bnc variant
            if corpus == 'bnc':
                pred_lab = bits[2]
                file = bits[0]
                corps.append(bits[1])
                fns.append(file)
            # rltc, croco variant
            elif corpus == 'cro' or corpus == 'rltc'  or corpus == 'joint':
                corps.append(bits[0])
                file = '_'.join(bits[:])
                fns.append(file)
                # on plain filenames, using INSTR to see how the clusters reflect the existing metadata
                ### this contition gets CroCo fns
                
                # this fails on rltc_pro
                # if re.match(r'[A-Z]', bits[1]):
                if bits[0] == 'EO':
                    # print(bits)
                    pred_lab = bits[1]
                elif bits[0] == 'en':
                    pred_lab = 'rltc_pro'
                # elif 'ps' in bits[1]:
                #     pred_lab = 'rltc_pro'
                # elif re.match(r'\d', bits[1]) and bits[0] != 'en':
                #     # print(bits)
                #     pred_lab = 'rltc_stu'
                elif bits[0] == 'EN':
                    pred_lab = 'rltc_stu'
            elif corpus == 'stu' or corpus == 'pro':
                if bits[0] == 'EN':
                    pred_lab = 'rltc_stu'
                elif bits[0] == 'en':
                    pred_lab = 'rltc_pro'
                file = '_'.join(bits[:])
                fns.append(file)
            else:
                print('Master and Commander! We are not sure which corpus do you mean? Your minions')
            # file = '_'.join(bits[:])
            # fns.append(file)
            current_cluster_preds.append(pred_lab)
        # convert the list to a freq dict, then to a regular dict and sort it
        # for preds
        freqs = dict(Counter(current_cluster_preds))
        freqs_sort = OrderedDict(sorted(freqs.items(), key=operator.itemgetter(1), reverse=True))
        for k, v in freqs_sort.items():
            print(k, v)

        # for corp membership
        corpsd = dict(Counter(corps))
        corpsd_sort = OrderedDict(sorted(corpsd.items(), key=operator.itemgetter(1), reverse=True))
        for k, v in corpsd_sort.items():
            print(k, v)
        if filenames:
            print(fns)
        clusters_dic[i] = fns
    
    ## to restore the picle run: clusters_files = pickle.load(open('/home/masha/clusters_fns', 'rb'))
    # pickle.dump(clusters_dic, open('/home/masha/venv/genre-keras/analysis/clusters_fns_%s' % corpus, 'wb'))
    
    return clusters_dic


# Cluster by Affinity Propagation (or other correlation matrix clustering algo)
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import SpectralClustering
from sklearn.cluster import DBSCAN  # Density-based spatial clustering of applications with noise (DBSCAN)
import matplotlib.pyplot as plt
from itertools import cycle
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


# the input should have real numbers (for plotting clusters) for indices and columns -- so use the array, not df_470
# algo: 'affinity','spectral'; name: name your text collection to cluster
# method of dim_reduction, model = NN? ML?
# experiment with the last two parameters: <=0.9, -5 (default)
def clustering_matrix(algo, array, fns, method, name, damping=0.9, preference=-5, plotting=0):
    # clustering from precomputed similarities, get 470 instances refered to numbered clusters (called labels 0,1,2,3 etc)
    
    # choose clustering algo
    if algo == 'affinity':
        clusterer = AffinityPropagation(damping=damping, preference=preference, affinity='precomputed', max_iter=200,
                                        verbose=True)
        af = clusterer.fit(array)
        cluster_centers_indices = af.cluster_centers_indices_  # Similar to k-medoids, finds "exemplars"
    
    if algo == 'spectral':
        clusterer = SpectralClustering(n_clusters=5, affinity='precomputed', assign_labels="kmeans", random_state=10)
        af = clusterer.fit(array)
    
    if algo == 'density':
        clusterer = DBSCAN(eps=0.3, min_samples=50, metric='precomputed')
        af = clusterer.fit(array)
    
    labels = af.labels_  # len 470
    n_clusters_ = len(set(labels))
    print('Estimated number of clusters: %d' % n_clusters_, file=sys.stderr)
    
    # lets do the simmat to a proper df and save to file
    df = pd.DataFrame(array)
    
    df.index = fns
    df.columns = fns
    df.name = name
    #     df.to_csv('%s_correlation_matrix.csv' % df.name, sep='\t')
    
    # add my_labels as a cluster column to df_470
    df['cluster'] = labels
    
    # get a Series with cluster number as index and lists of fns as column val from the df_470 'index' col
    # for that get a column with fns called 'index'
    df0 = df.reset_index()
    fn_series = df0.groupby('cluster')['index'].apply(list)
    
    # get counts of files (=rows) in each cluster
    sizes = df.groupby('cluster').size()
    
    # turn the Series to df and add cluster size column
    fn_df = fn_series.to_frame(name='files')
    fn_df.insert(0, 'size', sizes)
    
    # get fns for cluster centers indices and add this list as a col to df_470
    
    if algo == 'affinity':
        centers_fns = []
        for i in range(len(cluster_centers_indices)):
            center_fn = fns[cluster_centers_indices[i]]
            centers_fns.append(center_fn)
        fn_df.insert(0, 'center', centers_fns)
    else:
        pass
    
    fn_df = fn_df.sort_values(by=['size'], ascending=False)
    #     print(fn_df.head())
    
    # this plotting does not make sense for my data! it is only for 2-dim make_blobs toy_data!!!!
    # if I want any visualisation I need to reduce dimentionality
    if plotting:
        
        if method == 'pca':
            pca = PCA(n_components=2, random_state=50)
            sims_reduced = pca.fit_transform(array)
        
        if method == 'tsne':
            tsne = TSNE(perplexity=6, n_components=2, init='pca', n_iter=2500, random_state=23)
            sims_reduced = tsne.fit_transform(array)
        
        plt.close('all')
        plt.figure(1)
        plt.clf()
        #         print('Cluster center indices:', cluster_centers_indices)
        colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
        
        if algo == 'affinity':
            
            for k, col, center in zip(range(n_clusters_), colors, centers_fns):
                # 1-dim boolean array (470,) for the labels list
                class_members = labels == k
                
                plt.plot(sims_reduced[class_members, 0], sims_reduced[class_members, 1], col + '.')
                
                cluster_center = sims_reduced[cluster_centers_indices[k]]  # row of sims in the index
                #                 print('cluster_center', simmat_cosine_joint[108])
                plt.plot(cluster_center[0], cluster_center[1], 'o', label=center, markerfacecolor=col,
                         markeredgecolor='k', markersize=14)
                for x in sims_reduced[class_members]:
                    plt.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], col)
                    plt.annotate(center, (cluster_center[0], cluster_center[1]), fontsize=12)
        
        else:
            for k, col in zip(range(n_clusters_), colors):
                # 1-dim boolean array (470,) for the labels list
                class_members = labels == k
                plt.plot(sims_reduced[class_members, 0], sims_reduced[class_members, 1], col + '.')
        
        plt.title('%s estimated clusters for %s: %s' % (algo.upper(), df.name, n_clusters_))
        plt.show()
    
    return labels, fn_df, centers_fns


from sklearn.model_selection import train_test_split

from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.dummy import DummyClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import hamming_loss
from sklearn.model_selection import cross_val_predict
# from sklearn import cross_validation
from sklearn.model_selection import train_test_split
# from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_validate
from sklearn import tree

def classify_them_balanced(x, y):
    clf = RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight='balanced')
    #     clf = LogisticRegression
    # clf = tree.DecisionTreeClassifier()
    # clf = SVC(random_state=42, max_iter=10, verbose=False, class_weight='balanced') #
    #     clf = DummyClassifier(strategy='stratified', random_state=42)
    print(clf)  # this prints defaults of the classifier
    
    y_pred = cross_val_predict(clf, x, y, cv=10)
    # generate report
    print(classification_report(y, y_pred), file=sys.stderr)
   
    return y_pred


def classify_them(x, y, test=False, cv_report=False):
    clf = RandomForestClassifier(n_estimators=100, n_jobs=-1)
    #     clf = LogisticRegression
    # clf = tree.DecisionTreeClassifier()
    # clf = SVC(random_state=42, max_iter=10, verbose=False) #, class_weight='balanced'
    #     clf = DummyClassifier(strategy='stratified', random_state=42)
    
    print(clf)  # this prints defaults of the classifier
    
    if test:
        
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        # predict on unseen data
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)  # gets a list of class names
        acc1 = round(accuracy_score(y_test, preds), 3)  # ratio of correctly classified samples (int)
        f1 = round(f1_score(y_test, preds, average='macro'), 3)
        
        print("Classification report:\n", classification_report(y_test, preds))
        print("Fraction of correctly classified on the test set\t:", acc1)
        #     print('Macro-averaged recall:\t', av_recall)
        #     print('Macro-averaged F1:\t', f1)
        wrong_fraction = hamming_loss(y_test, preds)
        print("Proportion of misclassified:", wrong_fraction)
    else:
        print('Here goes cross-validation. Please wait a bit...', file=sys.stderr)
        averaging = 1  # Do you want to average the cross-validate metrics?
        
        scoring = ['precision_macro', 'recall_macro', 'f1_macro']
        # If you want a classification report really badly instead of all other metrics
        if cv_report:
            y_pred = cross_val_predict(clf, x, y, cv=10)
            # generate report
            print(classification_report(y, y_pred), file=sys.stderr)
        else:
            #             cv_scores = cross_val_score(clf, x, y, cv=10, scoring=scoring, n_jobs=2)
            cv_scores = cross_validate(clf, x, y, cv=10, scoring=scoring, n_jobs=2)
            if averaging:
                print("Average Precision on 10-fold cross-validation: %0.3f (+/- %0.3f)" % (
                    cv_scores['test_precision_macro'].mean(), cv_scores['test_precision_macro'].std() * 2),
                      file=sys.stderr)
                print("Average Recall on 10-fold cross-validation: %0.3f (+/- %0.3f)" % (
                    cv_scores['test_recall_macro'].mean(), cv_scores['test_recall_macro'].std() * 2), file=sys.stderr)
                print("Average F1 on 10-fold cross-validation: %0.3f (+/- %0.3f)" % (
                    cv_scores['test_f1_macro'].mean(), cv_scores['test_f1_macro'].std() * 2), file=sys.stderr)
            else:
                print("Precision values on 10-fold cross-validation:", file=sys.stderr)
                print(cv_scores['test_precision_macro'], file=sys.stderr)
                print("Recall values on 10-fold cross-validation:", file=sys.stderr)
                print(cv_scores['test_recall_macro'], file=sys.stderr)
                print("F1 values on 10-fold cross-validation:", file=sys.stderr)
                print(cv_scores['test_f1_macro'], file=sys.stderr)
        #     av_recall = round(recall_score(y_tst, preds, average='macro'), 3) #the average of recall obtained on each class
#     cla = clf.classes_
#     print(cla)
    return y_pred

def preprocess_n_classify(fns_dict, source_df): # source_df = original df with unlabelled data

    collector = []

    for k, v in fns_dict.items():
        cluster_slice = source_df.loc[v, :]
        cluster_slice['cluster'] = k
        collector.append(cluster_slice)
    final_df = pd.concat(collector)
    print(final_df.shape)

    print('How classifiable are my clusters? well not bad, ha?')
    Y = final_df['cluster']
    if 'corpus' in final_df.index:
        X = final_df.drop(['corpus', 'cluster'], axis=1)
    else:
        X = final_df.drop(['cluster'], axis=1)
    print(X.shape, Y.shape)
    y_pred = classify_them(X,Y,test=False, cv_report=True)
    
    return y_pred


def preprocess_folds(path, model, extention):
    outputs = [f for f in os.listdir(path) if f.endswith(extention)]
    ol = pd.DataFrame()
    for i in outputs:
        if model == 'mixed' and 'mix' in i:
            if extention == '.ann':
                fold_df = pd.read_csv(path + i, index_col='ID', sep='\t')
            else:
                fold_df = my_open(path + i)
            ol = ol.append(fold_df)
        if model == 'lex' and 'lex' in i:
            if extention == '.ann':
                fold_df = pd.read_csv(path + i, index_col='ID', sep='\t')
            else:
                fold_df = my_open(path + i)
            ol = ol.append(fold_df)
    
    # ## If the lengths of ol is greater than the number of instances, deduplicate?
    ol = ol[~ol.index.duplicated(keep='first')]  # get only the row not marked as duplicates
    print(ol.shape)
    print('surprisingly I dont get the expected 2211 instances from all folds')
    
    # ol = zero_out(ol)
    ol.name = 'cv_%s%s' % (model, extention)
    
    return ol