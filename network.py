import numpy as np
import random
import copy

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

    return nodes, neighbours


def SmallWorld(neighbours, number, elderly):
    # creates "working copy" of the neighbours dict
    bneighbours = copy.deepcopy(neighbours)
    keys = list(neighbours.keys())   # fetches a list of the nodes from the dictionary

    # picks SWLs twice: first for physical neighbours, then behavioural neighbours
    for x in range(2):
        for i in range(int(len(neighbours)*number[x])):
            pick1, pick2 = random.choices(keys, k=2)   # chooses two nodes at random

            # if picking for physical network...
            if x==0:
                while (pick2 in neighbours[pick1]):
                    pick1, pick2 = random.choices(keys, k=2)   # keep choosing if they are already neighbours
            elif x==1:
                while (pick2 in bneighbours[pick1]):
                    pick1, pick2 = random.choices(keys, k=2)   # keep choosing if they are already behavioural neighbours

            # if picking for physical network...
            if x == 0:
                # adds small world links to the list of neighbours
                neighbours[pick1].append(pick2)
                neighbours[pick2].append(pick1)

                # for the elderly special case, where there are no ring links but some contacts still need to be both physical and behavioural...
                if elderly==True:
                    if random.uniform(0.0,1.0)<0.5:   # make 50% of the physical links also be behavioural
                        bneighbours[pick1].append(pick2)
                        bneighbours[pick2].append(pick1)

            # if picking for behaviour network....
            else:
                # adds small world links to the list of neighbours
                bneighbours[pick1].append(pick2)
                bneighbours[pick2].append(pick1)

    return neighbours, bneighbours


def LinkRings(nbrs1, nbrs2, bnbrs1, bnbrs2, n, directional):
    # picking links for physical network...
    for i in range(int(n[0]*len(nbrs1))):
        node1 = random.choice(list(nbrs1.keys()))
        node2 = random.choice(list(nbrs2.keys()))

        # adds link to the list of neighbours
        nbrs1[node1].append(node2)
        nbrs2[node2].append(node1)

        if random.uniform(0,1)<0.5:   # make 50% of the physical links also be behavioural
            if directional!=True:   # the first ring passed is always the younger, so if the links are directional then don't add this neighbour
                bnbrs1[node1].append(node2)
            bnbrs2[node2].append(node1)


    # picking links for the behavioural network...
    for i in range(int(n[1]*len(bnbrs1))):
        node1 = random.choice(list(bnbrs1.keys()))
        node2 = random.choice(list(bnbrs2.keys()))

        # if the link already in the physical network or the behavioural network, pick again
        while (node2 in nbrs1[node1]) or (node2 in bnbrs1[node1]):
            node1 = random.choice(list(bnbrs1.keys()))
            node2 = random.choice(list(bnbrs2.keys()))
            
        # adds link to the list of neighbours
        if directional!=True:   # the first ring passed is always the younger, so if the links are directional then don't add this neighbour
            bnbrs1[node1].append(node2)
        bnbrs2[node2].append(node1)

    return nbrs1, nbrs2, bnbrs1, bnbrs2


def MakeNetworks(N1, N2, N3, factor):

    ################################ MAKING BASIC NODE NETWORK ################################

    # create the three (currently unattached) rings of nodes, plus the universal ring links
    nodes1, neighbours1 = CreateRing(0, N1, 1)   # this provides 2 disease links, 2 behavioural links
    nodes2, neighbours2 = CreateRing(N1, N1+N2, 1)   # this provides 2 disease links, 2 behavioural links
    nodes3, neighbours3 = CreateRing(N1+N2, N1+N2+N3,0)   # R3 has no systematic ring links, only random small world links

    ################################# ADDING SMALL WORLD LINKS ################################

    # adds small world links for disease and behavioural networks (boolean is for the elderly special case)
    neighbours1, bneighbours1 = SmallWorld(neighbours1, [(3.9*factor)-2, 0.9], False)   # this provides an additional 1.9 disease links, 0.9 behavioural links
    neighbours2, bneighbours2 = SmallWorld(neighbours2, [(3.5*factor)-2, 3.7], False)   # this provides an additional 1.5 disease links, 3.7 behavioural links
    neighbours3, bneighbours3 = SmallWorld(neighbours3, [(0.9*factor), 0.9], True)   # this provides an additional 0.9 disease links, 0.9 behavioural links


    ################################# ADDING INTER-RING LINKS ################################

    # link the three rings (number is the amount of links per node of the first set of nodes passed, e.g. R1 has 3.4*N1 physical links to R2)
    neighbours1, neighbours2, bneighbours1, bneighbours2 = LinkRings(neighbours1, neighbours2, bneighbours1, bneighbours2, [3.4*factor, 2.3], True)
    neighbours2, neighbours3, bneighbours2, bneighbours3 = LinkRings(neighbours2, neighbours3, bneighbours2, bneighbours3, [0.3*factor, 0.3], False)
    neighbours1, neighbours3, bneighbours1, bneighbours3 = LinkRings(neighbours1, neighbours3, bneighbours1, bneighbours3, [0.1*factor, 0.2], True)

    ####################################### MERGING INFO #####################################

    # merge individual rings' information into definitive lists
    nodes = np.ndarray.tolist(nodes1) + np.ndarray.tolist(nodes2) + np.ndarray.tolist(nodes3)
    neighbours = neighbours1 | neighbours2 | neighbours3
    bneighbours = bneighbours1 | bneighbours2 | bneighbours3

    # check results:
    #for node in neighbours:
        #print(node,'is physically connected to   ',neighbours[node])
        #print(node,'is behaviourally connected to',bneighbours[node])
    
    return nodes, neighbours, bneighbours