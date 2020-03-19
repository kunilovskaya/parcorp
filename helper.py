# this script contains modules to be imported to get EN-RU_comparable.py /
# that returns a list of filenames for texts from the second corpus that are found cross-linguistically most functionally similar to the first corpus

import numpy as np

import scipy.spatial as sp
import math
import operator
import pandas as pd
import sys
from collections import OrderedDict
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import SpectralClustering
from sklearn.cluster import DBSCAN  # Density-based spatial clustering of applications with noise (DBSCAN)
import matplotlib.pyplot as plt
from itertools import cycle
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


# this function can be used to compare different vectors for the same texts,
# so it will return a square matrix rather than 110X360 for texts from diff corpora
# can be fed dfs
def calc_sim(method, mat1, mat2):
    if method == 'cosine' or method == 'euclidean':
        sim_m = 1 - sp.distance.cdist(mat1, mat2, method)
        df = pd.DataFrame(sim_m)
        df.index = mat1.index
        df.columns = mat2.index
        average_sim = np.nanmean(sim_m)
        
    if method == 'dot':
        sim_m = np.dot(mat1, mat2.T)
        average_sim = sim_m.mean()
    # print('Based on functional representations from %s the input corpora have the similarity score of %0.3f (calculated as the averaged pair-wise %s similarity)' % (model, average_sim, method))
    return sim_m, average_sim

'''
Cluster by Affinity Propagation (or other correlation matrix clustering algo)
array: the data should have real numbers (for plotting clusters) for indices and columns -- so use the array, not df
algo: 'affinity','spectral', 'density'
fns: required to identify the cluster center and member-files; get the filenames from the df ID column

if plotting=1 (True)
experiment with the values of damping and preference parameters: <=0.9, -5 (default)
method: method for dimentionality reduction (if you want a 2D projection of your data as a plot
name: provide human-readable descriptive names for plotting (en, ru)
'''

def clustering_matrix(algo, array, fns, damping=0.9, preference=-5, plotting=0, method='pca', name='my data'):
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


# expects dfs of functional vectors for mat1 and mat2
def get_most_similar_texts(method='euclidian', centroid=None, mat1=None, mat2=None):
    sim_m = 1 - sp.distance.cdist(mat1, mat2, method)
    average_sim = np.nanmean(sim_m)

    fns = mat2.index.tolist()
    sims = {}
    list_of_vects = [mat2.loc[i, :].tolist() for i in mat2.index.tolist()]
    
    for idx, vect in enumerate(list_of_vects):
        euc_distance = 1 - math.sqrt(sum([(a - b) ** 2 for a, b in zip(centroid, vect)]))
        sims[fns[idx]] = euc_distance
    # sorted_x will be a list of tuples sorted by the second element in each tuple
    sorted_tuples_sims = sorted(sims.items(), key=operator.itemgetter(1), reverse=True)

    sorted_dict_sims = OrderedDict(sorted_tuples_sims)
    
    ordered_sim_fns = list(sorted_dict_sims.keys())
    sim_vals = list(sorted_dict_sims.values())
    
    print('Based on functional representations the input corpora have the similarity score of %0.4f (calculated as the averaged pair-wise %s similarity)' % (average_sim, method))
    return ordered_sim_fns, sim_vals

def get_top_filenames(similar=None, values=None, thres=0.7):
    for i, fn in enumerate(similar):
        if values[i] < thres:
            # print('Number of df2 files we can include into most similar (with eucledian similarity threshold >=%s: %s' % (thres, i-1))
            break
    print("The range for eucledian similarity is %.4f::%.4f" % (values[0], values[-1]))
    top = []
    for i, fn in enumerate(similar):
        if values[i] > thres:
            top.append(fn)
    return top