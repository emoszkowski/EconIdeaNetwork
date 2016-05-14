import pandas as pd
import networkx as nx
import numpy as np
import nltk.metrics as nm

####################################
# Parse Downloaded NBER CSV data   #
# into GRAPHML objects             #
# with edges as collaborations     #
# and correct year/JEL code labels #
####################################

######################################
# Read file from pipe-delimited file #
######################################

filepath = '../save/NBER_Paper_Info.csv'
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
authorLists = nber.authors.apply(lambda x: map(lambda x: x.strip(), x.split(',')))
maxLength = max(authorLists.apply(lambda x: len(x)))

# Index into Variable, but return NaN if out of bounds
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
# b/c they throw off our merge
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

#################################################
# Add JEL Codes and Years to Coauthorship Edges #
#################################################

nberCartChars = pd.merge(nberCart, nber[['title','jel','year']], how='left', on='title')
nberCartChars.jel = nberCartChars.jel.apply(lambda x: x.replace(', ',','))

# Need [author_x, author_y, {'jel':JEL, 'year':YEAR}]

nberEdges = [[r[1],r[2],{'jel':r[3],'year':r[4],'title':r[0]}] for r in \
             nberCartChars.values]

################
# Create Graph #
################

# Generate Blank Graph
G = nx.MultiGraph()

# Add Authors
authors = nberCartChars.value_x.unique()
G.add_nodes_from(authors)

# Add Edges
G.add_edges_from(nberEdges)

# TODO: Add Department Attribute (WIP)

#################
# Write to File #
#################

outpath = '../save/nber.graphml'
nx.write_graphml(G, outpath)

#############################
# Degree Distribution       # 
#############################
degree_dist = nx.degree_histogram(G)

#######################################
# Calculate distribution of JEL codes #
# for each author                     #
#######################################

# how many unique JEL codes are there?
jelList = ','.join(list(nberCartJEL.jel))
jelList = jelList.split(',')
jelSet = set(jelList)

# make a JEL lookup table
jelLookup = dict()
for i, jel in enumerate(jelSet):
    jelLookup[jel] = i

# make an array of authors x JELs to keep counts
authors = nx.nodes(G) 
authorCodes = np.zeros((len(authors), len(jelSet)))
for a in range(len(authors)):
    papers = G.edges(authors[a])
    for p in papers:
        paperAttrs = G.get_edge_data(p[0], p[1])
        paperJels  = paperAttrs['jelcode'].split(',')
        jelInds = [jelLookup[jel] for jel in paperJels]
        authorCodes[a, jelInds] += 1

#####################
# Compute PageRank  # 
#####################

ranks = nx.pagerank(G)

# add to graph
nx.set_node_attributes(G, 'rank', ranks)

# in case we want to look at the top authors
sortedRanks = sorted(ranks.items(), key=lambda x: x[1])


########################
# Feature matrix       #
########################

# Extract PageRank to a vector
nodeRanks = np.empty(len(authors))
for i in range(len(authors)):
    nodeRanks[i] = ranks.get(authors[i])
nodeRanks = np.reshape(nodeRanks, (len(nodeRanks),1))

# Make a dataFrame
data = np.hstack((nodeRanks,authorCodes))
df = pd.DataFrame(data)
df.columns = ['rank'] + [jel for jel in jelSet]
df['author'] = authors
