'''
task: detect wc (or char-count outliers) for each subcorpus
An outliers is a text that significantly deviates (given a parameter: ex. text length (wc), average sentence-length) from the average in the corpus
Approaches:
(1) percentile-based measure: calculetes datapoints within a pre-set threshold (by default: 5%) at each side of a distribution;
(2) Median Absolute deviation (MAD) is based on z-score calculated from mean and median values.

This helps to capture texts with the formatting issues or extreme stylistic diversity

USAGE: python3 get_outliers.py --corpus /path/to/corpus/ --parameter sent_length --method percentile --thres 90
'''

import sys, os
import numpy as np
import argparse
from smart_open import open

import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from array import *


##### OUR FUNCTIONS #####

def collect_wc(corpus):
    names = []
    nums = []
    
    files = [f for f in os.listdir(corpus) if f.endswith('.txt')]
    for f in files:
        text = open(corpus + f, 'r').readlines()
        words = 0
        for s in text:
            text_split = s.split()
            words += len(text_split)
        names.append(f)
        nums.append(words)
    aver = np.mean(nums)
    
    return names, nums, aver


def collect_sent_lengths(corpus):
    names = []
    nums = []
    files = [f for f in os.listdir(corpus) if f.endswith('.txt')]
    for f in files:
        text = open(corpus + f, 'r').readlines()
        words = 0
        sentences = len(text)
        for s in text:
            text_split = s.split()
            words += len(text_split)
        fstat = float(words) / sentences
        names.append(f)
        nums.append(fstat)
    aver = np.mean(nums)
    
    return names, nums, aver


# percentile-based
def percentile_based_outlier(data, threshold=None):  # discards 5% of outliers at each side
    diff = (100 - threshold) / 2.0
    minval, maxval = np.percentile(data, [diff, 100 - diff])  # calculate upper and lower boundary
    return (data < minval) | (data > maxval)


# MAD
def is_outlier(points, thresh=2):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation = MAD) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    if len(points.shape) == 1:
        points = points[:, None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median) ** 2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)
    
    modified_z_score = 0.6745 * diff / med_abs_deviation
    
    return modified_z_score > thresh


#### MAIN CODE ######
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', help="Path to one-sent-per-line files", required=True)
    parser.add_argument('--parameter', default='sent_length', help="What's your criteria for detecting outliers: wc (sample size); or sent_length")
    parser.add_argument('--method', type=str, default='percentile', help='Chose: percentile (requires an interger for threshold!) or MAD')
    parser.add_argument('--thres', type=int, default=90, help='This is the threshold for the percentile method')
    args = parser.parse_args()

    my_corpus = args.corpus
    parameter = args.parameter
    method = args.method
    # for percentile select the ratio of texts to retain (90% by default)
    thres = 90
    
    if parameter == 'wc':
        fnames, vals, mean = collect_wc(my_corpus)
    
    elif parameter == 'sent_length':
        fnames, vals, mean = collect_sent_lengths(my_corpus)
    
    else:
        fnames, vals, mean = None, None, None
        print('Select your parameter')
    # convert the list of values to a 1-D array
    arr = np.array(vals)
    if method == 'percentile':
        barr = percentile_based_outlier(arr, threshold=thres)
    elif method == 'mad':
        barr = is_outlier(arr)  # gets result from MAD
    else:
        barr = None
        print('Select your method')
    
    items = len(fnames)
    
    count = 0
    if method == 'wc':
        print('outlier filename\twc')
    elif method == 'sent_length':
        print('outlier filename\tsent_length')
    for k in range(items):
        if barr[k] == True:
            count += 1
            print(fnames[k], '\t', arr[k])
        else:
            continue
    print('Corpus average %.2f' % mean)
    print('Number of %s outliers (based on %s): %d' % (method, parameter, count))
