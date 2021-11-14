# 1. Make a network
# 2. Simulate disease spread on the network
# 3. Simulate gradual vaccine uptake 

######################################### IMPORTS #########################################

import random
import numpy as np
import matplotlib.pyplot as plt

def Event(type, time, primary, secondary):
    if type=='trans':
        event={'type':type,
                'time':time,
                'primary':primary,
                'secondary':secondary}
    else:
        event={'type':type,
                'time':time,
                'node':primary}

    return event

def PlotOutbreakSize(values):
    bin_edges = np.arange(0.5, max(values)+0.5, 1)   # creates array of histogram bin edges ±0.5 of each integer outbreak size
    plt.hist(values, bins=bin_edges, label='N=100 nodes')   # draws histogram of outbreak sizes
    plt.xlabel("Outbreak size")
    plt.ylabel("Frequency")
    plt.title("Distribution of outbreak sizes for "+str(len(values))+" simulated \n outbreaks, with one vaccination for each infection")
    plt.legend()
    plt.show()

def main():
    #################################### MAKE NETWORK #####################################
    # define number of nodes and make an array of nodes
    N=100
    nodes=np.arange(0,N,1)

    # make a list of edges (nodes are connected to those that are close to them)
    edges=[]
    for i in nodes:
        # for each node i, make two (3-1=2) new edges
        for j in range(1,3):
            j=(i+j)%N   # use the modular function (% in python) to wrap network around
            edges.append((i,j))   # add the edge to the list

    # store the network links as a dictionary
    neighbours={}
    for node in nodes:   # each entry will be a list, one for every node
        neighbours[node]=[]   # start with a dictionary of empty lists
        
    # add the network neighbours of each node
    for i,j in edges:
        neighbours[i].append(j)   # add j to i's neighbours 
        neighbours[j].append(i)   # add i to j's neighbours

    # check the results
    #for node in neighbours: 
        #print(node,'is connected to',neighbours[node])

    ############################ DEFINE SIMULATION PARAMETERS #############################
    # define some parameters
    beta=0.5   # the probability that an infected node infectes a susceptible neighbour
    seed=0   # start with a seed node (patient zero)

    # generation times are drawn from the log normal distribution defined below...
    g_mode=5 
    g_dispersion=1.3
    g_sigma=np.log(g_dispersion)
    g_mu=(g_sigma**2)+np.log(g_mode)

    # vaccination effectiveness times are drawn from the log normal distribution defined below
    v_mode=5 
    v_dispersion=1.3
    v_sigma=np.log(v_dispersion)
    v_mu=(v_sigma**2)+np.log(v_mode)

    ################################## SIMULATE OUTBREAK ##################################
    # create a list to store the sizes of X simulated outbreaks
    X = 100000
    outbreak_sizes=[]

    # run X simulations to collect outbreak sizes
    for i in range(1,X+1):
        # we will keep an array telling us the immunity status of each node
        # for initial conditions we start with all nodes susceptible (all values false)
        immune=np.zeros(N, dtype=bool)

        # create a list of events. this list will grow and shrink over time
        events=[]

        # each event is a small dictionary with keys...
        # type: the type of event which occurs
        # time: the time that the event occurs 
        # primary: the node that is doing the infecting
        # secondary: the node that is being infected

        # create the first event (the seeding event) and add to events list
        events.append(Event('trans', 0, None, seed))

        # output is a tree-like network
        tree=[]

        # start a loop in which we resolve the events in time order until no events remain
        while events:
            event=min(events,key=lambda x: x['time'])   # fetch earliest infection event on the list
            events.remove(event)   # remove the chosen infection from the list
            
            # if the selected event is a transmission...
            if event['type']=='trans':
                # ignoring cases in which the secondary is already immune (so no infection occurs)...
                if not immune[event['secondary']]:
                    #print(str(event['primary'])+' infected '+str(event['secondary'])+' at t = '+str(event['time']))   # print the event
                    tree.append((event['primary'],event['secondary']))   # add event to the tree

                    # now we need to add more infections to the list...
                    primary=event['secondary']   # "move on" so that the secondary becomes the new primary
                    immune[primary]=True   # make the primary immune so that no future events can affect that node
                    
                    # create new infection events to add to the list
                    for secondary in neighbours[primary]:   # for all neighbours of the primary...
                        if random.random()<beta and not immune[secondary]:   # determines if primary infects secondary
                            generation_time=int((24*60*60)*np.random.lognormal(g_mu,g_sigma))   # how long will it be (in seconds) until primary infects secondary?
                            transmission_time=event['time']+generation_time   # adds generation period to previous event time to give current event time

                            # create the event
                            events.append(Event('trans', transmission_time, primary, secondary))

                    if len(nodes[immune==False])>0:
                        pick_index = np.random.randint(0, len(nodes[immune==False]))
                        pick = nodes[immune==False][pick_index]
                        immune[pick]=True
                        events.append(Event('vax', transmission_time, pick, None))
                        #print(pick,"got vaccinated!")

            elif event['type']=='vax':
                effective_time=int((24*60*60)*np.random.lognormal(v_mu,v_sigma))
                end_time=event['time']+effective_time
                immune[event['node']]=False
                #print(event['node'],"become susceptible again!")
                events.append(Event('unvax', end_time, event['node'], None))
                
        print("Outbreak "+str(i)+" size = "+str(len(tree)))
        outbreak_sizes.append(len(tree))   # append outbreak size to list for plotting later
    PlotOutbreakSize(outbreak_sizes)

main()