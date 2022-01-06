# 1. Make a network
# 2. Simulate disease spread on the network
# 3. Simulate gradual vaccine uptake 

######################################### IMPORTS #########################################

import csv
import random
import numpy as np
import matplotlib.pyplot as plt
import os

import network as nw
import vaccination as vx

################################### AUXILIARY FUNCTIONS ###################################

# function to make a dictionary for any event type
def Event(type, time, primary, secondary):
    # each event is a small dictionary with keys...
            # type: the type of event which occurs
            # time: the time that the event occurs 
            # primary: the node that is doing the infecting
            # secondary: the node that is being infected

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
    ############################ DEFINE SIMULATION PARAMETERS #############################
    
    # define number of nodes in each age group (proportions from 2019 https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/articles/overviewoftheukpopulation/january2021#the-uks-population-is-ageing)
    totalN = 10000
    N1 = int(0.19*totalN)
    N2 = int(0.625*totalN)
    N3 = int(totalN-(N1+N2))

    time_period = (7*24*60*60)   # defines the amount of time to count 'recent' cases (for plotting). default is 1 week

    vax_type = 'random'   # can be 'random', 'agebased', or 'sequential'
    
    # define how many links are made between rings (arbitrary numbers for now)
    link1to2 = int(N1*1.75)
    link2to3 = int(N2*0.85)
    link1to3 = int(N3*0.8)

    beta=0.5   # the probability that an infected node infects a susceptible neighbour
    seed=N1+1   # start with a seed node (patient zero), the first "adult" node

    # generation times (in days) are drawn from the log normal distribution defined below...
    g_mode=5 
    g_dispersion=1.3
    g_sigma, g_mu = LogNormal(g_mode, g_dispersion)

    # post-covid immunity times (in days) are drawn from the log normal distribution defined below...
    c_mode=180 
    c_dispersion=10
    c_sigma, c_mu = LogNormal(c_mode, c_dispersion)

    # vaccination effectiveness times (in days) are drawn from the log normal distribution defined below...
    v_mode=180
    v_dispersion=10
    v_sigma, v_mu = LogNormal(v_mode, v_dispersion)

    ################################## SIMULATE OUTBREAK ##################################
    print("\n-------------- NODE NUMBERS -------------")
    print("Total nodes: " + str(totalN))
    print("U16s: "+str(N1)+", 16-64s: "+str(N2)+", 65+: "+str(N3)+"\n")

    nodes, edges, neighbours = nw.DiseaseNetwork(N1, N2, N3, link1to2, link2to3, link1to3)

    # create a list to store the sizes of X simulated outbreaks
    X = 20

    file = open('active_cases_data.csv','w')
    
    # only write header if the file is new (otherwise, just append new data)
    #if os.stat('active_cases_data.csv').st_size == 0:
    file.write("Active cases, Time (s) \n")

    #vax_frac = 0.5   # (i*10)% of the total nodes will be vaccinated at random (FOR RANDOMVAX)

    # run X simulations to collect outbreak sizes 
    for j in range(1):
        immune=np.zeros(totalN, dtype=bool)   # an array telling us the immunity of each node (for initial conditions we start with all nodes susceptible)
        tree=[]   # output is a tree-like network

        events=[]   # create a list of events (this list will grow and shrink over time)
        events.append(Event('trans', 0, None, seed))   # create the first transmission event (the seeding event) and add to events list
        
        #events = vx.RandomVax(vax_frac, totalN, events)   # randomly chooses a given % of nodes to be vaccinated at a random time in the first year
        events = vx.AgeWaveVax(0.75, N1, N2, N3, events)

        case_numbers = []
        active_cases = []

        # start a loop in which we resolve the events in time order until no events remain
        while events:
            event=min(events,key=lambda x: x['time'])   # fetch earliest infection event on the list
            events.remove(event)   # remove the chosen infection from the list
            
            # if the selected event is a transmission...
            if event['type']=='trans':
                # ignoring cases in which the secondary is already immune (so no infection occurs)...
                if not immune[event['secondary']]:
                    print("\U0001F534" + str(event['primary'])+' infected '+str(event['secondary'])+' at '+ConvertTime(event['time']))   # print the event
                    tree.append((event['primary'],event['secondary']))   # add event to the tree

                    active_cases.append(event)

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
                print("\U0001F7E2" + str(event['node']) + " got vaccinated at " + ConvertTime(event['time']))

                end_time = NewEventTime(event['time'], v_mu, v_sigma)
                events.append(Event('unvax', end_time, event['node'], None))   # creates 'unvax' event and adds to list

            elif event['type']=='unvax':
                immune[event['node']]=False   # node is no longer immune
                #print("\U0001F7E0" + str(event['node']) + " became re-susceptible after vaccination at " + ConvertTime(event['time']))

            elif event['type']=='resusceptible':
                immune[event['node']]=False
                #print("\U0001F7E1" + str(event['node']) + " became re-susceptible after infection at " + ConvertTime(event['time']))

            # removes events from recents if it is older than the specified time_period (typically a week)

            active_cases = [item for item in active_cases if item['time'] > (event['time']-time_period)]

            if len(active_cases)!=0:
                case_numbers.append((len(active_cases), event['time']))
                file.write(str(len(active_cases))+"," + str(event["time"]) + "\n")

        infected = []
        for x in range(len(tree)):
            infected.append(tree[x][1])

        print("--- OUTBREAK STATS ---")

        print("Number of infections: "+str(len(tree)))
        print("Number of nodes infected: "+str(len(set(infected))))
        print("Last infection occurred at "+str(ConvertTime(lastinfection))+"\n")
    

    file.close()

main()