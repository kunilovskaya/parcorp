
# calculate average feature values for each corpus to compare them
# use the bigtable.tsv output by ud_extractor (or any tab-separated spreadsheet where rows are texts and columns are features; adjust to drop non-numeric columns)

# USAGE: python3 stats/bigtable_overview.py stats/tables/good_ud_stats.tsv good


import sys
import csv
import pandas as pd
import numpy as np

stats = sys.argv[1]
name = sys.argv[2]

bigtable = pd.read_csv(stats, sep='\t') # reads into a DataFrame: rows of index and values

bigtable0 = bigtable.drop(['doc', 'group'], 1)  # drop string values cols
header = ['Feature','Average','Deviation','Observations']

with open('stats/tables/overview_%s.tsv' % name, "w") as outfile:
	writer = csv.writer(outfile, delimiter="\t")
	writer.writerow(header)
	for col in bigtable0.columns:
		line = [col, np.average(bigtable0[col]), np.std(bigtable0[col]), len(bigtable0[col])]
		writer.writerow(line)
