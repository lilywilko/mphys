import numpy as np
import random

def CreateRing(start, N):
    nodes=np.arange(start,N,1)
    # make a list of edges (nodes are connected to those that are close to them)
    edges=[]
    for i in nodes:
        # for each node i, make two (3-1=2) new edges
        for j in range(1,3):
            j=((i+j)%N)   # use the modular function (% in python) to wrap network around
            if j==0 or j==1:
                if start!=0:
                    j=j+start
            edges.append((i,j))   # add the edge to the list

    neighbours={}
    for node in nodes:
        neighbours[node]=[]

    # add the network neighbours of each node
    for i,j in edges:
        neighbours[i].append(j)   # add j to i's neighbours 
        neighbours[j].append(i)   # add i to j's neighbours

    return nodes, edges, neighbours


def AddSmallWorld(neighbours):
    keys = list(neighbours.keys())   # fetches a list of the nodes from the neighbours dictionary
    pick1, pick2 = random.choices(keys, k=2)   # chooses two nodes at random

    # adds small world links to the list of neighbours
    neighbours[pick1].append(pick2)
    neighbours[pick2].append(pick1)

    return neighbours


def LinkRings(nbrs1, nbrs2, n):
    for i in range(n):
        node1 = random.choice(list(nbrs1.keys()))
        node2 = random.choice(list(nbrs2.keys()))

        # adds small world links to the list of neighbours
        nbrs1[node1].append(node2)
        nbrs2[node2].append(node1)

    return nbrs1, nbrs2