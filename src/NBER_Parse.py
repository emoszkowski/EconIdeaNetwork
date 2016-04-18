import pandas as pd
import networkx as nx
import numpy as np
import nltk.metrics as nm

######################################
# Read file from pipe-delimited file #
######################################

filepath = '../save/NBER_Paper_Info.1.csv'
nber = pd.read_csv(filepath, delimiter='|')

####################
# Initial Cleaning #
####################

# Drop 'Jr.'
nber.authors = nber.authors.apply(lambda x: x.replace(', Jr.',''))
nber.authors = nber.authors.apply(lambda x: x.replace(', Jr',''))
nber.authors = nber.authors.apply(lambda x: x.replace(' Jr.',''))
nber.authors = nber.authors.apply(lambda x: x.replace(' Jr',''))

# Separate List of Authors
authorLists = nber.authors.apply(lambda x: x.split(','))
maxLength = max(authorLists.apply(lambda x: len(x)))

def safeindex(x, i):
    try:
        return x[i]
    except:
        return np.nan

for i in range(maxLength):
    nber['author' + str(i)] = authorLists.apply(lambda x: safeindex(x,i))

#####################################
# Create long table of paper-author #
#####################################

cols = ['title'] + [c for c in nber.columns if \
                    'author' in c and 'authors' not in c]
nberLong = pd.melt(nber[cols], id_vars=['title'])
nberLong = nberLong[~pd.isnull(nberLong.value)][['title','value']]

# Drop middle names and punctuation 
# b/c they throw off
def dropMiddle(x):
    xSplit = x.strip().split(' ')
    if len(xSplit) < 3:
        return ''.join(xSplit)
    else:
        return ''.join([xSplit[0],xSplit[-1]])
nberLong.value = nberLong.value.apply(dropMiddle)
nberLong.value = nberLong.value.apply(lambda x: x.replace('.',''))

#######################################
# create Cartesian product to extract #
# coauthorship graph edges            #
#######################################

nberCart = pd.merge(nberLong, nberLong, how='outer', on='title')
nberCart = nberCart[nberCart.value_x != nberCart.value_y]

#######################################
# Add JEL Codes to Coauthorship Edges #
#######################################

nberCartJEL = pd.merge(nberCart, nber[['title','jel']], how='left', on='title')
nberCartJEL.jel = nberCartJEL.jel.apply(lambda x: x.replace(', ',','))

nberEdges = list(nberCartJEL.value_x + '|' + nberCartJEL.value_y + '|' + nberCartJEL.jel)

################
# Create Graph #
################

G = nx.parse_edgelist(nberEdges, delimiter='|', data=(('jelcode',str),))

# Add Department Attribute (WIP)

#################
# Write to File #
#################

outpath = '../save/nber.graphml'
nx.write_graphml(G, outpath)
