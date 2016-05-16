## Utility functions

# getJELSubgraph generates the subgraph of G containing all papers with 
# JEL code 'jelcode'
def getJELSubgraph(G, jelcode):
    SG = nx.Graph()
    sge = [e for e in G.edges(data=True) if jelcode in e[2]['jel']]
    sge = map(lambda x: [jel.upper() for jel in x[2]['jel']], sge)
    SG.add_edges_from(sge)

# getBigJELSubgraph generates the subgraph of G containing all papers with 
# JEL category (first letter) 'jelcode'
def getBigJELSubgraph(G, jelcode):
    SG = nx.Graph()
    sge = [e for e in G.edges(data=True) if jelcode in re.findall("[a-zA-Z]", e[2]['jel'])]
    SG.add_edges_from(sge)
    return SG

# Returns the Mean all-pairs node connectivity of a JEL Code
def getConnEst(G, jelcode):
    return np.mean(nx.all_pairs_node_connectivity(getJELSubgraph(G, jelcode)).values()[0].values()) 

# Returns set of all JEL codes that appear over all edges of G.
def getJELs(G):
    return set(','.join([x[2]['jel'].upper() for x in G.edges(data=True)]).split(','))

# Get set of JEL super-categories (just first letter)
def getBigJELs(jels):
    bigJels = map(lambda x: re.findall("[a-zA-Z]", x)[0].upper(), jels)
    return set(bigJels)

# Check for matches (authors that appear multiple times) using Levenstein Distance (tolerance = 2)
def getAuthorMatches(author,allAuthors):

    matches = pd.DataFrame(allAuthors.author[allAuthors.author.apply(lambda x: editdistance.eval(x, author)) < 2])
    matches['repecAuthor'] = author

    return matches

    
