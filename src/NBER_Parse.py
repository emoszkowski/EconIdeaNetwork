import pandas as pd
import networkx as nx
import numpy as np

######################################
# Read file from pipe-delimited file #
######################################

filepath = '../save/NBER_Paper_Info.1.csv'
nber = pd.read_csv(filepath, delimiter='|')

# First step: Create coauthorship graph

# Convert nber authors into edgelist
authorLists = nber.authors.apply(lambda x: x.split(','))

maxLength = max(authorLists.apply(lambda x: len(x)))

def safeindex(x, i):
    try:
        return x[i]
    except:
        return np.nan

for i in range(maxLength):
    nber['author' + str(i)] = authorLists.apply(lambda x: safeindex(x,i))

# reshape to long
cols = ['title'] + [c for c in nber.columns if \
                    'author' in c and 'authors' not in c]
nberLong = pd.melt(nber[cols], id_vars=['title'])
nberLong = nberLong[~pd.isnull(nberLong.value)][['title','value']]
nberLong.value = nberLong.value.apply(lambda x: x.replace(' ',''))

# create Cartesian product
nberCart = pd.merge(nberLong, nberLong, how='outer', on='title')
nberCart = nberCart[nberCart.value_x != nberCart.value_y]

# Create Edge List
nberEdges = list(nberCart.value_x + '|' + nberCart.value_y)
G = nx.parse_edgelist(nberEdges, delimiter='|')

# Write to File
outpath = '../save/nber.graphml'
nx.write_graphml(G, outpath)
