import numpy as np
import random

def CreateRing(start, N, number):
    nodes=np.arange(start,N,1)
    # make a list of edges (nodes are connected to those that are close to them)
    edges=[]
    for i in nodes:
        # for each node i, make two (3-1=2) new edges
        for j in range(1,number+1):
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


def SmallWorld(neighbours, number):
    keys = list(neighbours.keys())   # fetches a list of the nodes from the neighbours dictionary

    for i in range(int(len(neighbours)*number)):
        pick1, pick2 = random.choices(keys, k=2)   # chooses two nodes at random

        while (pick2 in neighbours[pick1]):
            pick1, pick2 = random.choices(keys, k=2)   # keep choosing if they are already neighbours

        # adds small world links to the list of neighbours
        neighbours[pick1].append(pick2)
        neighbours[pick2].append(pick1)

    return neighbours


def LinkRings(nbrs1, nbrs2, n):
    for i in range(int(n*len(nbrs1))):
        node1 = random.choice(list(nbrs1.keys()))
        node2 = random.choice(list(nbrs2.keys()))

        # adds small world links to the list of neighbours
        nbrs1[node1].append(node2)
        nbrs2[node2].append(node1)

    return nbrs1, nbrs2


def MakeNetworks(N1, N2, N3):
    nodes, edges, neighbours = DiseaseNetwork(N1, N2, N3)
    bnodes, bedges, bneighbours = BehaviourNetwork(nodes, edges, neighbours)

    return nodes, edges, neighbours, bnodes, bedges, bneighbours


def DiseaseNetwork(N1, N2, N3):
    # POLYMOD stats for age groups:
    # Internal ring links: R1=3.9, R2=3.5, R3=0.9

    # create the three (currently unattached) rings of nodes
    nodes1, edges1, neighbours1 = CreateRing(0, N1, 1)
    nodes2, edges2, neighbours2 = CreateRing(N1, N1+N2, 1)
    nodes3, edges3, neighbours3 = CreateRing(N1+N2, N1+N2+N3,0)   # R3 has no systematic ring links, only random small world links

    # adds small world links within each ring (second number is the number of links per node)
    neighbours1 = SmallWorld(neighbours1, 1.9)
    neighbours2 = SmallWorld(neighbours2, 1.5)
    neighbours3 = SmallWorld(neighbours3, 0.9)

    # link the three rings (number is the amount of links per node of the first set of nodes passed, e.g. R1 has 3.4*N1 links to R2)
    neighbours1, neighbours2 = LinkRings(neighbours1, neighbours2, 3.4)
    neighbours2, neighbours3 = LinkRings(neighbours2, neighbours3, 0.3)
    neighbours1, neighbours3 = LinkRings(neighbours1, neighbours3, 0.1)

    # merge individual rings' information into definitive lists
    nodes = np.ndarray.tolist(nodes1) + np.ndarray.tolist(nodes2) + np.ndarray.tolist(nodes3)
    edges = edges1 + edges2 + edges3
    neighbours = neighbours1 | neighbours2 | neighbours3

    # check results:
    #for node in neighbours:
        #print(node,'is connected to',neighbours[node])

    return nodes, edges, neighbours


def BehaviourNetwork(nodes, edges, neighbours):
    return nodes, edges, neighbours