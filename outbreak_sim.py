# 1. Make a network
# 2. Simulate disease spread on the network
# 3. Simulate gradual vaccine uptake 

######################################### IMPORTS #########################################

import random
import numpy as np
import matplotlib.pyplot as plt
import os

import network as nw
import vaccination as vax
import voter_model as vm

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
    totalN = 1000
    N1 = int(0.19*totalN)
    N2 = int(0.625*totalN)
    N3 = int(totalN-(N1+N2))

    time_period = (7*24*60*60)   # defines the amount of time to count 'recent' cases (for plotting). default is 1 week

    #vax_type = 'random'   # can be 'random', 'agebased', or 'sequential'

    SWLpercent = 0.5

    # selects a determined amount of nodes to be seeds
    seed_no = 5
    patients_zero = random.sample(range(0, totalN), seed_no)

    # generation times (in days) are drawn from the lognormal distribution defined below...
    g_mode=5 
    g_dispersion=1.3
    g_sigma, g_mu = LogNormal(g_mode, g_dispersion)

    # post-covid immunity times (in days) are drawn from the lognormal distribution defined below...
    c_mode=180 
    c_dispersion=10
    c_sigma, c_mu = LogNormal(c_mode, c_dispersion)

    # vaccination effectiveness times (in days) are drawn from the lognormal distribution defined below...
    v_mode=180
    v_dispersion=10
    v_sigma, v_mu = LogNormal(v_mode, v_dispersion)


    # case severity is drawn from an age-based lognormal distribution defined below...
    R1_sigma = 0.6
    R1_mu = 0.2

    R2_sigma = 0.6
    R2_mu = 0.6

    R3_sigma = 0.5
    R3_mu = 1.1

    ################################## SIMULATE OUTBREAK ##################################

    print("\n-------------- NODE NUMBERS -------------")
    print("Total nodes: " + str(totalN))
    print("U16s: "+str(N1)+", 16-64s: "+str(N2)+", 65+: "+str(N3)+"\n")


    # creates separate disease and behaviour networks (currently identical)
    nodes, neighbours, bneighbours = nw.MakeNetworks(N1, N2, N3)

    # collects the amounts of neighbours that each node has
    neighbour_nos = []
    for i in range(len(neighbours)):
        neighbour_nos.append(len(neighbours[i]))

    # forces R0 to be 1.5 using the randomly generated neighbours (beta * avg. neighbours = R0 = 1.5)
    beta=1.5/np.mean(np.asarray(neighbour_nos))
    #vax_frac = 0.5   # (i*10)% of the total nodes will be vaccinated at random (FOR RANDOMVAX)

    X = 1
    # run X simulations to collect outbreak sizes 
    for j in range(X):

        # status arrays
        immune=np.zeros(totalN, dtype=bool)   # an array telling us the immunity of each node (for initial conditions we start with all nodes susceptible)
        
        av_frac = 0.2   # varies the fraction of voters who are initialised to be anti-vax
        opinions = np.zeros(totalN, dtype=bool)   # an array keeping track of everyone's behaviour status
        for i in range(totalN):
            roll = random.uniform(0.0, 1.0)   # randomly initialises a pro/anti-vax stance for each node
            if roll>av_frac:
                opinions[i]=1   # ZERO IS ANTI-VAX, ONE IS PRO-VAX

        severity=np.zeros(totalN)   # an array keeping track of everyone's most severe case of disease
        case_nos=np.zeros(totalN)

        tree=[]   # output is a tree-like network

        events=[]   # create a list of events (this list will grow and shrink over time)

        for i in range(seed_no):
            events.append(Event('trans', 0, None, patients_zero[i]))   # create the first transmission event (the seeding event) and add to events list

        events.append(Event('kill', 365*24*60*60, None, None))   # creates an event to cut the simulation short at one year
        
        #events = vax.RandomVax(vax_frac, totalN, events)   # randomly chooses a given % of nodes to be vaccinated at a random time in the first year
        #events = vax.AgeWaveVax(1, N1, N2, N3, events)
        #events = vax.LogDistVax(1, totalN, events)

        #events = vm.GetOpinionEvents(N1, N2, N3, events)   # creates totalN*5 events for a random node to potentially change opinion at a random time

        case_numbers = []
        active_cases = []

        # counts how many vaccinations and vaccine refusals have occurred
        vax_count = 0
        refuse_count = 0

        # flags for when resusceptibility and vaccination kick in
        resus_active = 0
        resus_time = 0
        vax_active = 0
        vax_time = 0

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

                    case_severity=2   # trick to ensure that chosen case severity is a maximum of 1...
                    while case_severity>1:
                        # if infected node is a child...
                        if event['secondary']<N1:
                            case_severity = np.random.lognormal(R1_mu,R1_sigma)
                        # if infected node is an adult...
                        elif event['secondary']<N1+N2:
                            case_severity = np.random.lognormal(R2_mu,R2_sigma)
                        # if infected node is elderly...
                        else:
                            case_severity = np.random.lognormal(R3_mu,R3_sigma)

                        case_severity = case_severity/8   # scale factor for severities
                    
                    if case_severity>severity[event['secondary']]:
                        severity[event['secondary']]= case_severity   # updates "most severe case" if necessary

                    active_cases.append(event)
                    case_nos[event['secondary']]+=1

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
                if opinions[event['node']] == 1:   # if the node is pro-vax (denoted 1)...
                    immune[event['node']]=True   # makes the node immune
                    vax_count+=1
                    print("\U0001F7E2" + str(event['node']) + " got vaccinated at " + ConvertTime(event['time']))

                else:
                    refuse_count+=1
                    print("\U0001F535" + str(event['node']) + " refused the vaccine at " + ConvertTime(event['time']))

                if vax_active==0:
                    vax_active = 1
                    vax_time = event['time']

                end_time = NewEventTime(event['time'], v_mu, v_sigma)
                events.append(Event('unvax', end_time, event['node'], None))   # creates 'unvax' event and adds to list

            elif event['type']=='opinion':
                if len(bneighbours[event['node']])>0:   # clause to avoid breaking on nodes with no neighbours
                    neighbourpick = random.choice(bneighbours[event['node']])   # chooses a random neighbour

                    # if the potential opinion change is from pro-vax to anti-vax, check extra conditions...
                    if opinions[neighbourpick]==False and opinions[event['node']]==True:

                        # checks if any neighbours had a "severe" case (above 0.8)
                        checker=False
                        for i in range(len(bneighbours[event['node']])):
                            if severity[bneighbours[event['node']][i]]>0.8 and checker==False:
                                checker=True

                        # if the node or its neighbours have had a severe case, reduce switch probability from 100% to 15%
                        if severity[event['node']]>=0.8 or checker==True:
                            roll = random.uniform(0.0, 1.0)
                            if roll>0.85:
                                opinions[event['node']] = opinions[neighbourpick]

                        # if the node and its neighbours have not had severe case, switch opinion as usual
                        else:
                            opinions[event['node']] = opinions[neighbourpick]

                    else:
                            opinions[event['node']] = opinions[neighbourpick]

            elif event['type']=='unvax':
                immune[event['node']]=False   # node is no longer immune
                print("\U0001F7E0" + str(event['node']) + " became re-susceptible after vaccination at " + ConvertTime(event['time']))

            elif event['type']=='resusceptible':
                immune[event['node']]=False
                print("\U0001F7E1" + str(event['node']) + " became re-susceptible after infection at " + ConvertTime(event['time']))

                if resus_active==0:
                    resus_active=1
                    resus_time=event['time']

            # when the 'kill' event is reached, delete all future events and finish the simulation
            elif event['type']=='kill':
                events=[]

            # removes events from recents if it is older than the specified time_period (typically a week)
            active_cases = [item for item in active_cases if item['time'] > (event['time']-time_period)]

            if len(active_cases)!=0:
                case_numbers.append((len(active_cases), event['time']))

            # kills the simulation early once there are no more vaccinations to be performed
            #if len(list(filter(lambda item: item['type'] == 'vax', events)))==0:
                #events=[]

            # displays a changing readout of the voter model balance
            print("Anti-vax:" + str(sum(i == 0 for i in opinions)) + ", pro-vax: " + str(sum(i == 1 for i in opinions)) + ". Run no. " + str(j+1) + " of " + str(X), end='\r')

        infected = []
        for x in range(len(tree)):
            infected.append(tree[x][1])

        print(" ")
        print("--- OUTBREAK STATS ---")

        print("Number of infections: "+str(len(tree)))
        print("Number of nodes infected: "+str(len(set(infected))))
        print("Last infection occurred at "+str(ConvertTime(lastinfection))+"\n")

    filename = 'active_cases_POLYMOD.csv'
    file = open(filename,'a')
    for i in range(len(case_nos)):
        file.write(str(case_numbers[i][0]) + "," + str(case_numbers[i][1])+",7\n")
    file.close()

main()