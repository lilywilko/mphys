# 1. Make a network
# 2. Simulate disease spread on the network
# 3. Simulate gradual vaccine uptake 

################################### IMPORTS #####################################

import random
import numpy as np

############################### 1. MAKE NETWORK #################################

# define number of nodes and make a list of nodes
N=100
nodes=list(range(N))

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
#print()

######################### 2. SIMULATE DISEASE SPREAD ############################

# define some parameters
beta=0.5   # the probability that an infected node infectes a susceptible neighbour
seed=0   # start with a seed node (patient zero)

# generation times are drawn from the log normal distribution defined below...
mode=5 
dispersion=1.3
sigma=np.log(dispersion)
mu=(sigma**2)+np.log(mode)

# we will keep a dictionary telling us the immunity status of each node
immune={}

# for initial conditions we start with all nodes susceptible
for node in nodes:
    immune[node]=False
    
# create a list of events. this list will grow and shrink over time
events=[]

# each event is a small dictionary with keys...
# type: the type of event which occurs
# time: the time that the event occurs 
# primary: the node that is doing the infecting
# secondary: the node that is being infected

# define the first event (the seeding event)
first_infection={'type':'trans',
            'time':0,
             'primary':None,
             'secondary':seed}

# add this to the list
events.append(first_infection)

# output is a tree-like network
tree=[]

# start a loop in which we resolve the events in time order until no events remain
while events:
    event=min(events,key=lambda x: x['time'])   # fetch earliest infection event on the list
    events.remove(event)   # remove the chosen infection from the list
    
    # ignoring cases in which the secondary is already immune (so no infection occurs)...
    if not immune[event['secondary']]:
        print(str(event['primary'])+' infected '+str(event['secondary'])+' at t = '+str(event['time']))   # print the event
        tree.append((event['primary'],event['secondary']))   # add event to the tree

        # now we need to add more infections to the list...
        primary=event['secondary']   # "move on" so that the secondary becomes the new primary
        immune[primary]=True   # make the primary immune so that no future events can affect that node
        
        # create new infection events to add to the list
        for secondary in neighbours[primary]:   # for all neighbours of the primary...
            if random.random()<beta and not immune[secondary]:   # determines if primary infects secondary
                generation_time=int((24*60*60)*np.random.lognormal(mu,sigma))   # how long will it be (in seconds) until primary infects secondary?
                transmission_time=event['time']+generation_time   # adds generation period to previous event time to give current event time

                # create the event
                new_event={'type':'trans',
                        'time':transmission_time,
                        'primary':primary,
                        'secondary':secondary}
                events.append(new_event) # add event to the list
        
print() 
print('Outbreak size = '+str(len(tree)))