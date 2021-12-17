# 1. Make a network
# 2. Simulate disease spread on the network
# 3. Simulate gradual vaccine uptake 

######################################### IMPORTS #########################################

import random
import numpy as np
import matplotlib.pyplot as plt

import network as nw

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
def PlotOutbreakSize(values, i, n):
    colours = ['maroon', 'red', 'darkorange', 'gold', 'limegreen', 'turquoise', 'deepskyblue', 'darkblue', 'indigo', 'darkviolet', 'violet']
    #bin_edges = np.arange(0.5, max(values)+0.5, 1)   # creates array of histogram bin edges ±0.5 of each integer outbreak size
    plt.hist(values, bins=40, label=str(i*10)+"% vax", histtype='step', color=colours[i])   # draws histogram of outbreak sizes
    plt.xlabel("Outbreak size")
    plt.ylabel("Frequency")
    plt.title("Distribution of outbreak sizes for "+str(len(values))+" simulated outbreaks \n on a network of "+str(n)+" nodes")


# function to return the next event time
def NewEventTime(time, mu, sigma):
    wait=int((24*60*60)*np.random.lognormal(mu,sigma))   # how long will it be (in seconds) until the next event?
    return time+wait


def ConvertTime(time):
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    return str(day)+" days, "+str(hour)+" hours, "+str(minutes)+" minutes, and "+str(seconds)+" seconds"


def LogNormal(mode, dispersion):
    sigma=np.log(dispersion)
    mu=(sigma**2)+np.log(mode)
    return sigma, mu


def main():
    #################################### MAKE NETWORK #####################################
    
    # define number of nodes in each age group (proportions from 2019 https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/articles/overviewoftheukpopulation/january2021#the-uks-population-is-ageing)
    totalN = 500
    N1 = int(0.19*totalN)
    N2 = int(0.625*totalN)
    N3 = int(totalN-(N1+N2))

    print("U16s: "+str(N1)+", 16-64s: "+str(N2)+", 65+: "+str(N3))

    # define how many links are made between rings
    link1to2 = 30
    link2to3 = 30
    link1to3 = 30

    # create the three (currently unattached) rings of nodes
    nodes1, edges1, neighbours1 = nw.CreateRing(0, N1)
    nodes2, edges2, neighbours2 = nw.CreateRing(N1, N1+N2)
    nodes3, edges3, neighbours3 = nw.CreateRing(N1+N2, totalN)

    # add one small world link to each ring
    neighbours1 = nw.SmallWorld(neighbours1)
    neighbours2 = nw.SmallWorld(neighbours2)
    neighbours3 = nw.SmallWorld(neighbours3)

    # link the three rings
    neighbours1, neighbours2 = nw.LinkRings(neighbours1, neighbours2, link1to2)
    neighbours2, neighbours3 = nw.LinkRings(neighbours2, neighbours3, link2to3)
    neighbours1, neighbours3 = nw.LinkRings(neighbours1, neighbours3, link1to3)

    # merge individual rings' information into definitive lists
    nodes = np.ndarray.tolist(nodes1) + np.ndarray.tolist(nodes2) + np.ndarray.tolist(nodes2)
    edges = edges1 + edges2 + edges3
    neighbours = neighbours1 | neighbours2 | neighbours3

    # check the results
    #for node in neighbours: 
        #print(node,'is connected to',neighbours[node])

    ############################ DEFINE SIMULATION PARAMETERS #############################
    # define some parameters
    beta=0.5   # the probability that an infected node infectes a susceptible neighbour
    seed=0   # start with a seed node (patient zero)

    # generation times (in days) are drawn from the log normal distribution defined below...
    g_mode=5 
    g_dispersion=1.3
    g_sigma, g_mu = LogNormal(g_mode, g_dispersion)

    # post-covid immunity times (in days) are drawn from the log normal distribution defined below
    c_mode=180 
    c_dispersion=10
    c_sigma, c_mu = LogNormal(c_mode, c_dispersion)

    # vaccination effectiveness times (in days) are drawn from the log normal distribution defined below
    v_mode=180
    v_dispersion=10
    v_sigma, v_mu = LogNormal(g_mode, g_dispersion)

    ################################## SIMULATE OUTBREAK ##################################
    # create a list to store the sizes of X simulated outbreaks
    X = 1
    outbreak_sizes=np.zeros((11,X))

    # run simulation with 11 different vaccination amounts (0%, 10%, 20% etc to 100%)
    for i in range(11):
        # i% of the total nodes will be vaccinated at random
        print("Running for " + str(i*10) + "%...")
        vax_events = int((i/10)*totalN)

        # run X simulations to collect outbreak sizes 
        for j in range(X):
            print("Run no. " + str(j), end="\r")
            # we will keep an array telling us the immunity status of each node
            # for initial conditions we start with all nodes susceptible (all values false)
            immune=np.zeros(totalN, dtype=bool)

            # create a list of events. this list will grow and shrink over time
            events=[]

            # each event is a small dictionary with keys...
            # type: the type of event which occurs
            # time: the time that the event occurs 
            # primary: the node that is doing the infecting
            # secondary: the node that is being infected

            # create the first event (the seeding event) and add to events list
            events.append(Event('trans', 0, None, seed))

            
            # picking a node to vaccinate....
            picked=np.zeros(totalN, dtype=bool)
            for x in range(vax_events):
                unvaxxed = np.where(picked==False).nonzero()
                pick = np.random.choice(unvaxxed)   # picks a random non-immune node
                print(pick)
                vax_time = np.random.randint(0,31536000)   # picks a random second within the first year to vaccinate
                events.append(Event('vax', vax_time, pick, None))   # creates a vax event and adds to the list
            
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
                        #print(str(event['primary'])+' infected '+str(event['secondary'])+' at '+ConvertTime(event['time']))   # print the event
                        tree.append((event['primary'],event['secondary']))   # add event to the tree

                        # now we need to add more infections to the list...
                        primary=event['secondary']   # "move on" so that the secondary becomes the new primary
                        immune[primary]=True   # make the primary immune so that no future events can affect that node
                        
                        # create new infection events to add to the list
                        for secondary in neighbours[primary]:   # for all neighbours of the primary...
                            if random.random()<beta and not immune[secondary]:   # determines if primary infects secondary
                                transmission_time = NewEventTime(event['time'], g_mu, g_sigma)   # when will the primary infect the secondary?
                                events.append(Event('trans', transmission_time, primary, secondary))   # creates the transmission event and adds to list

                                resusceptible_time = NewEventTime(transmission_time, c_mu, c_sigma)
                                events.append(Event('resusceptible', resusceptible_time, secondary, None))

                    # if there are no more transmission events in the events list...
                    if len(list(filter(lambda e: e['type'] == 'trans', events)))==0:
                        lastinfection = event['time']   # store the time of the final transmission

                # if the earliest remaining event is a vaccination...
                elif event['type']=='vax':
                    immune[event['node']]=True   # makes the vaxxed node immune
                    #print(event['node'],"got vaccinated at",ConvertTime(event['time']))

                    end_time = NewEventTime(event['time'], v_mu, v_sigma)
                    events.append(Event('unvax', end_time, event['node'], None))   # creates 'unvax' event and adds to list

                elif event['type']=='unvax':
                    immune[event['node']]=False   # node is no longer immune
                    #print(event['node'], "became re-susceptible after vaccination at", ConvertTime(event['time']))

                elif event['type']=='resusceptible':
                    immune[event['node']]=False
                    #print(event['node'], "became re-susceptible after infection at", ConvertTime(event['time']))

            infected = []
            for x in range(len(tree)):
                infected.append(tree[x][1])

            print("--- OUTBREAK "+str(i+1)+" (" + str(i*10) + "% VACCINATION) STATS ---")

            print("Number of infections: "+str(len(tree)))
            print("Number of nodes infected: "+str(len(set(infected))))
            print("Last infection occurred at", ConvertTime(lastinfection))
            
            outbreak_sizes[i][j]=len(tree)   # append vaxxed outbreak size to list for plotting later

    #for i in range(11):
        #PlotOutbreakSize(outbreak_sizes[i], i, totalN)   # plots and shows the distribution of outbreak sizes
    #PlotOutbreakSize(outbreak_vaxxed, 'One vax event per infection event', N)   # plots and shows the distribution of outbreak sizes
    #plt.legend(loc="upper left")
    #plt.show()

main()