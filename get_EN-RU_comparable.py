'''
This script aims to reduce a random subset of ru_araneum corpus (4.9K texts) to a genre-comparable reference corpus for Yandex paralle web corpus (429 text pairs)
(1) represent STs from a parallel corpus with fvectors
(2) detect clusters in it or assume that it is homogeneous
'''

import numpy as np
import pandas as pd

# my functions
from helper import calc_sim, clustering_matrix, get_most_similar_texts, get_top_filenames


def get_meanFTDs(df):
    dfm = df.copy()
    dfm.loc['Mean',:] = df.mean(axis=0)
    res = dfm.loc['Mean', :]
    print('Average values on FTDs for %s' % df.name)
    return res


# Apply round off setting to whole notebook
np.set_printoptions(precision=3)

df1 = pd.read_csv('models/en_yandex_predicted_main.res', index_col='ID', sep='\t').sort_index()
df2 = pd.read_csv('models/ru_araneum_predicted_main.res', index_col='ID', sep='\t').sort_index()
df1.name = 'en'
df2.name = 'ru'
print(df1.head(3))

# print(get_meanFTDs(df1))
# print(get_meanFTDs(df2))


# measure internal corpus similarity (= homogeneity): get a square matrix of pairwise sims for each corpus
simmat1, mean1 = calc_sim('euclidean', df1, df1)
# print(simmat1.shape)
print('Homogeneity EN: %.4f' % mean1)
simmat2, mean2 = calc_sim('euclidean', df2, df2)
# print(simmat2.shape)
print('Homogeneity RU: %.4f' % mean2)


# apply affinity propagation clustering algorithm to the square matrices;
# it will estimate the optimal number of clusters based on preference value that you provide (the greater negative value the less clusters)
'''
HOWTO:
# array: the data should have real numbers (for plotting clusters) for indices and columns -- so use the array, not df
# algo: 'affinity','spectral', 'density'
# fns: required to identify the cluster centers; get the filenames from the df ID column

# if plotting=1 (True)
# experiment with the values of damping and preference parameters: <=0.9, -5 (default)
# method: method for dimentionality reduction (if you want a 2D projection of your data as a plot
# name: provide human-readable descriptive names for plotting (en, ru)
'''

labels_en, clustered_en, centers_en = clustering_matrix('affinity', simmat1, df1.index.tolist(),
                                     damping=0.9, preference=-10, plotting=0, name='en')
print(clustered_en[['size', 'center']])
# uncomment if running for the first time
# labels_ru, clustered_ru, centers_ru = clustering_matrix('affinity', simmat2, df2.index.tolist(),
#                                      damping=0.9, preference=-10, plotting=0, name='ru')
# print(clustered_ru[['size', 'center']])

# get N most similar df2 (ru) texts to the df2 (en) targeted cluster centroid
# look at the output of the previous step and extract the vectors of the cluster centroids from df1 on which you want to limit df2
cenroid_cl1 = df1.loc['en_yandexweb_778000.txt', :].tolist()
cenroid_cl2 = df1.loc['en_yandexweb_510000.txt', :].tolist()
cenroid_cl3 = df1.loc['en_yandexweb_316000.txt', :].tolist()

print(cenroid_cl3)

# get lists of df2 texts most similar to df1 clusters cenroids
similars1, values1 = get_most_similar_texts(method='euclidean', centroid=cenroid_cl1, mat1=df1, mat2=df2)
similars2, values2 = get_most_similar_texts(method='euclidean', centroid=cenroid_cl2, mat1=df1, mat2=df2)
similars3, values3 = get_most_similar_texts(method='euclidean', centroid=cenroid_cl3, mat1=df1, mat2=df2)

sim_threshold = 0.65

# for each df1 cluster:
top1 = get_top_filenames(similar=similars1, values=values1, thres=sim_threshold)
print(len(top1))
top2 = get_top_filenames(similar=similars2, values=values2, thres=sim_threshold)
print(len(top2))
top3 = get_top_filenames(similar=similars3, values=values3, thres=sim_threshold)
print(len(top3))

print('Total number of df2 texts similar to the representative diversity of df1:', len(top1)+len(top2)+len(top3))
all_fns = top1+top2+top3
# uncomment to get the list of the most_similar texts filenames
# print(all_fns)
# or save to a file:
with open('reduce_araneum_to_443texts.fns', 'w') as out:
    for i in all_fns:
        i = i.strip()
        out.write(i + '\n')

