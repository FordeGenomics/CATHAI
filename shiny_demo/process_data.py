#!/usr/bin/env python3
import json, os, glob
import pandas as pd
import networkx as nx

def sortSTs(elem):
    if elem == 'NA':
        return 0
    else:
        return int(elem.replace('ST', ''))

def get_species(date):
    species = set()
    speciesST = {}
    date = date + '/'

    for sample in glob.glob(distDir + date + "*" + distExt):
        sample = sample.split(date)[1]
        name, ST = sample.split('_ST', 1)
        name = name.replace('_', ' ')
        species.add(name)
        if name not in speciesST:
            speciesST[name] = set()
        ST = ST.split(distExt)[0]
        if '_' in ST:
            ST = 'NA'
        speciesST[name].add(ST)

    species = sorted(list(species))

    for key in speciesST:
        speciesST[key] = sorted(list(speciesST[key]), key=sortSTs)

    return species, speciesST

def genDistName(species, ST):
        ret = species.replace(' ', '_')
        ret = ret + '_'
        if 'ST' not in ST:
            ret = ret + 'ST_NA'
        else:
            ret = ret + ST
        ret = ret + distExt
        return ret

#def getNetwork(species, ST, date, metadata):
#    input = distDir + str(date) + '/' + genDistName(species, ST)
#    if not (os.path.exists(input) and os.path.isfile(input)):
#        print("species/st not in selected date")
#        return None
#
#    output=input+".json"
#    if (os.path.exists(output) and os.path.isfile(output)):
#        with open(output, 'r') as f:
#            elements = json.load(f)
#    else:
#        elements = genNetwork(species, ST, date, metadata)
#        with open(output, 'w') as f:
#            json.dump(elements, f)
#
#    return elements

def genNetwork(species, ST, date, metadata):
    input = distDir + str(date) + '/' + genDistName(species, ST)
    print("input: " + input)
    if not (os.path.exists(input) and os.path.isfile(input)):
        print("species not in selected date")
        return None, None
    A = pd.read_csv(input, sep='\t', index_col=0, header=0)
    if len(A.columns) == 0:
        A = pd.read_csv(input, sep=',', index_col=0, header=0)

    cols = list(A.columns)
    fixed_cols = []
    for col in cols:
      fixed_cols.append(col.replace("-", "_"))

    rows = list(A.index)
    fixed_rows = []
    for row in rows:
      fixed_rows.append(row.replace("-", "_"))

    A.columns = fixed_cols
    A.index = fixed_rows

    def inverse(x):
        if x == 0:
            return 1
        else:
            return 1/x
    
    def sqRt(x):
        if x == 0:
            return 0
        else:
            return math.sqrt(x)
    
    A = A.applymap(inverse)
    G = nx.from_pandas_adjacency(A)
    pos=nx.fruchterman_reingold_layout(G, iterations=20000, threshold=1e-10)
  
    Wed=[]
    XYed=[]
    edgeData={}
    nodeData={}

    for edge in G.edges:
        Wed.append(G.edges[edge]['weight'])
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        XX = (x0, x1)
        YY = (y0, y1)
        XY = (XX, YY)
        XYed.append(XY)
    
    edgeData['weight'] = Wed
    edgeData['xy'] = XYed

    nodeData['text'] = [node for node in G.nodes]
    nodeData['Xn'] = [pos[k][0] for k in G.nodes]
    nodeData['Yn'] = [pos[k][1] for k in G.nodes]

    for node in G.nodes:
      if node not in list(metadata.index):
        print(f"ERROR: Sample {node} not found in metadata.csv. Using NA metadata values.")
        metadata = metadata.append(pd.Series(name=node, dtype=str))
        metadata['ID'][node] = node
        metadata['Species'][node] = species
        metadata['MLST (ST)'][node] = ST
        metadata = metadata.fillna('')

    for key in metadata.keys():
        nodeData[key] = [metadata[key][k] for k in G.nodes]

    return edgeData, nodeData

def genDistName(species, ST):
        ret = species.replace(' ', '_')
        ret = ret + '_'
        if ST == 'NA':
            ST = '_NA'
        ret = ret + 'ST' + ST
        ret = ret + distExt
        return ret

##### Main code
distDir = "./data/"
distExt = ".snpDists"

data_dirs = []
dates = []
for d in sorted(os.listdir(distDir), reverse=True):
    bd = os.path.join(distDir, d)
    if os.path.isdir(bd):
        date = os.path.basename(bd)
        data_dirs.append(date)
        dates.append(date[4:6] + '/' + date[2:4] + '/20' + date[0:2])

latest_data = str(max(data_dirs, key=os.path.basename))
metadata=pd.read_csv(distDir + latest_data + '/metadata.csv', index_col=0, dtype=str, keep_default_na=False)
metadata.insert(0, 'ID', metadata.index)
metadata.insert(len(metadata.columns), 'intDate', metadata['sample date'].apply(lambda x: x.replace('-', '')))

species, speciesST = get_species(latest_data)
print("latest_data: " + latest_data)

for s in speciesST.keys():
  for st in speciesST[s]:
    input = distDir + str(latest_data) + '/' + genDistName(s, st)
    output=input+".json"
    elements = genNetwork(s, st, latest_data, metadata)
    with open(output, 'w') as f:
      json.dump(elements, f)
