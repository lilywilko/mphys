# 1. Make a network
# 2. Simulate disease spread on the network
# 3. Simulate gradual vaccine uptake 

######################################### IMPORTS #########################################

import random
import numpy as np
import matplotlib.pyplot as plt

################################### AUXILIARY FUNCTIONS ###################################

# function to make a dictionary for any event type
def Event(type, time, primary, secondary):
    # if the event is a transmission...
    if type=='trans':
        event={'type':type,
                'time':time,
                'primary':primary,   # primary is the node that does the infecting
                'secondary':secondary}   # secondary is the node that is infected

    # if the event is a vaccination, 'unvax' (vaccination wearing off) or "resusceptible" (post-covid immunity wearing off)...
    else:
        event={'type':type,
                'time':time,
                'node':primary}   # primary is used to indicate the node (secondary will be passed as None)

    return event

# function to plot the distribution of outbreak sizes
def PlotOutbreakSize(values, status, n):
    bin_edges = np.arange(0.5, max(values)+0.5, 1)   # creates array of histogram bin edges ±0.5 of each integer outbreak size
    plt.hist(values, bins=bin_edges, label=status, histtype='step')   # draws histogram of outbreak sizes
    plt.xlabel("Outbreak size")
    plt.ylabel("Frequency")
    plt.title("Distribution of outbreak sizes for "+str(len(values))+" simulated outbreaks \n on a network of "+str(n)+" nodes")

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

    # post-covid immunity times are drawn from the log normal distribution defined below
    #c_mode=5 
    #c_dispersion=1.3
    #c_sigma=np.log(c_dispersion)
    #c_mu=(c_sigma**2)+np.log(c_mode)

    # vaccination effectiveness times are drawn from the log normal distribution defined below
    v_mode=5 
    v_dispersion=1.3
    v_sigma=np.log(v_dispersion)
    v_mu=(v_sigma**2)+np.log(v_mode)

    # choose how many random cells will be vaccinated
    vax_events = 0.05*N

    ################################## SIMULATE OUTBREAK ##################################
    # create a list to store the sizes of X simulated outbreaks
    X = 1
    outbreak_sizes=[]
    outbreak_vaxxed=[]

    # run simulation twice through (once with vaccination, then once without vaccination)
    for i in range(2):
        # run X simulations to collect outbreak sizes
                        
        for j in range(1,X+1):
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

            # including vaccination on the first runthrough only...
            if i==0:
                print("--- VACCINATION LIST ---")
            # picking a node to vaccinate....
                for x in range(vax_events):
                   pick = np.random.randint(1, N)   # picks a random non-immune node
                   vax_time = np.random.randint(0,10000000)
                   events.append(Event('vax', vax_time, pick, None))   # creates a vax event and adds to the list
                   print(pick, "will be vaccinated at", vax_time)

            print("------------------------")
<<<<<<< HEAD

=======
            
>>>>>>> 24850977be4759773e1434228d280d896be323c7
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
                        print(str(event['primary'])+' infected '+str(event['secondary'])+' at t = '+str(event['time']))   # print the event
                        tree.append((event['primary'],event['secondary']))   # add event to the tree

                        # now we need to add more infections to the list...
                        primary=event['secondary']   # "move on" so that the secondary becomes the new primary
                        immune[primary]=True   # make the primary immune so that no future events can affect that node
                        
                        # create new infection events to add to the list
                        for secondary in neighbours[primary]:   # for all neighbours of the primary...
                            if random.random()<beta and not immune[secondary]:   # determines if primary infects secondary
                                generation_time=int((24*60*60)*np.random.lognormal(g_mu,g_sigma))   # how long will it be (in seconds) until primary infects secondary?
                                transmission_time=event['time']+generation_time   # adds generation period to previous event time to give current event time
                                events.append(Event('trans', transmission_time, primary, secondary))   # creates the transmission event and adds to list

                                #immunity_time=int((24*60*60)*np.random.lognormal(c_mu,c_sigma))
                                #resusceptible_time=event['time']+immunity_time
                                #events.append(Event('resusceptible', resusceptible_time, secondary, None))

                # if the earliest remaining event is a vaccination...
                elif event['type']=='vax':
                    immune[event['node']]=True   # makes the vaxxed node immune
                    effective_time=int((24*60*60)*np.random.lognormal(v_mu,v_sigma))   # how long will the vaccine be effective for (in seconds)?
                    end_time=event['time']+effective_time   # adds effective period to vaccination time to give current event time
                    events.append(Event('unvax', end_time, event['node'], None))   # creates 'unvax' event and adds to list
                    print(event['node'],"got vaccinated!")

                elif event['type']=='unvax':
                    immune[event['node']]=False   # node is no longer immune
                    print(event['node'], "became re-susceptible after vaccination!")

                #elif event['type']=='resusceptible':
                    #immune[event['node']]=False
                    #print(event['node'], "became re-susceptible after infection!")
                    
            print("Outbreak "+str(j)+" size = "+str(len(tree)))
            
            if i==0:
                outbreak_vaxxed.append(len(tree))   # append no-vax outbreak size to list for plotting later
            else:
                outbreak_sizes.append(len(tree))   # append vaxxed outbreak size to list for plotting later

    PlotOutbreakSize(outbreak_sizes, 'No vaccinations', N)   # plots and shows the distribution of outbreak sizes
    PlotOutbreakSize(outbreak_vaxxed, 'One vax event per infection event', N)   # plots and shows the distribution of outbreak sizes
    plt.legend()
    plt.show()

main()