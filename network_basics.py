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
        j=(i+j)%N   # use the modular function (% in python) to wrap around
        edges.append((i,j))   # add the edge to the list
        
#check to see what that loks like
print(edges)
print()

# for contagion models its useful to store the network links as a dictionary
# start with an empty dictionary
neighbours={}
# each entry will be a list, one for every node, 
for node in nodes:
    # start with a dictionary of empty lists
    neighbours[node]=[]
    
# now add the network neighbours of each node
for i,j in edges:
    # add j to i's neighbours 
    neighbours[i].append(j)
    # add i to j's neighbours
    neighbours[j].append(i)

# check the results
for node in neighbours: 
    print(node,'is connected to',neighbours[node])
print()

######################### 2. SIMULATE DISEASE SPREAD ############################

# Define some parameters
# beta is the proability that an infected node infectes a susceptible neighbour
beta=0.5
# start with a seed node
seed=0
# the generation times are drawn from a distribution
mode=5 
dispersion=1.3,
sigma=np.log(dispersion)
mu=(sigma**2)+np.log(mode)

# we will keep a dictionarytelling us the status of each node
# start with an empty dictionary
immune={}
# for initial conditions we start with all of them susceptible
for node in nodes:
    immune[node]=False
    
# create a list of events. This list will grow and shrink over time
events=[]

# each event is a small dictionary with keys
# time: the time that the event occurs 
# primary: the node that is infected
# scondary: the node that 

# the first event is the seeding event
first_infection={'type':'trans',
            'time':0,
             'primary':None,
             'secondary':seed}

# add this to the list
events.append(first_infection)

# output is a tree-like network
tree=[]

# now we start a loop in which we resolve the events in time order
# until there are no events remaining
while events:
    
    # take the first event from the list 
    # get earliest infection event on the list
    event=min(events,key=lambda x: x['time'])
    # remove the chosen infection from the list
    events.remove(event)
    
    # in some cases the secondary might already be immune
    # if that is the case we ignore this and go to the next step
    if not immune[event['secondary']]:
        # print out the event:
        print(str(event['primary'])+' infected '+str(event['secondary'])+' at t='+str(event['time']))
        # add it to the tree
        tree.append((event['primary'],event['secondary']))
        # now we need to add more infections to the list
        primary=event['secondary']
        # make the primary immune so that no future events can affect them
        immune[primary]=True
        
        # create new infection events to add to the list
        for secondary in neighbours[primary]:
            # does primary infect seconday?
            if random.random()<beta and not immune[secondary]:
                # how long will it be until primary infects secondary
                generation_time=int((24*60*60)*np.random.lognormal(mu,sigma))
                # so the time of the transmission will be...
                transmission_time=event['time']+generation_time
                # create the event
                new_event={'time':transmission_time,
                           'primary':primary,
                           'secondary':secondary}
                # add it to the list
                events.append(new_event) 
        
        
print() 
print('outbreak size='+str(len(tree)))


 
 





