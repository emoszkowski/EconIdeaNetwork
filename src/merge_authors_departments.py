# ## Import NBER graph and add department data

import pandas as pd
import networkx as nx
import numpy as np
import scipy.stats as stats
import nltk.metrics as nm
import editdistance
import re
import matplotlib.pyplot as plt

execfile("utils.py")

# Load NBER Graph from File
# NBER graph contains coauthorship edges annotated with JEL codes 
path = '../save/nber.graphml'
G = nx.read_graphml(path)

# Get List of JEL codes
# e = G.edges(data=True)
jels = getJELs(G) 
bigJels = getBigJELs(jels)

# Get list of nodes from NBER graph
n = G.nodes()
ndf = pd.DataFrame(n, columns=['author'])

## Read departments (scraped from REPEC) in to dataframe
department = pd.read_csv('../../../work_erica/EconIdeaNetwork/save/REPEC_Paper_Info.csv', delimiter=',')
department = department.drop_duplicates()

department['authorClean'] = department.Author.apply(lambda x: x.replace(',','').split(' '))
department['authorClean'] = department['authorClean'].apply(lambda x: x[1] + x[0])

# HACK: If an author appears in 2 departments, drop duplicates by
# taking first institution that appears
department = department.groupby('authorClean').first().reset_index()

authorDF = []

# Get list of author names that appear in REPEC and NBER datasets
deptMatches = department.authorClean.apply(lambda x: getAuthorMatches(x,ndf))
deptMatches = pd.concat(list(deptMatches))

# Fix author errors in NBER by merging nodes with name errors (typos, etc)
s = deptMatches.groupby('repecAuthor').size()
nberAuthorErrors = s[s > 1].index

for currAuthor in nberAuthorErrors:

    # For each duplicate name (modulo Levenstein distance 2):
    # 1. collect all edges (including attributes) from both duplicates
    # 2. delete node
    # 3. add back a new node with all edges and attributes from the 2 previous nodes

    prevAuthorNames = deptMatches[deptMatches.repecAuthor == currAuthor].author.values
    allPrevEdges = []
    allPrevEdgeAttributes = []

    for prevName in prevAuthorNames:

        prevEdges = G.edges(prevName, data=True)
        prevEdges = [x[1] for x in prevEdges]
        prevEdgeAttributes = [x[2] for x in prevEdges]

        allPrevEdges = allPrevEdges + prevEdges
        allPrevEdgeAttributes = allPrevEdgeAttributes + prevEdgeAttributes
        
        G.remove_node(prevName)

    for i,target in enumerate(allPrevEdges):
        G.add_edge(prevAuthorNames[0], target, jel=allPrevEdgeAttributes[i])

# Merge department affiliations onto author matches
authDept = pd.merge(deptMatches, department, how='left', left_on='repecAuthor', right_on='authorClean')

# Save G and authDept to files
outpath = '../save/authors_departments.graphml'
nx.write_graphml(G, outpath)

authDept.to_csv("../save/authors_departments.csv",sep='|')
