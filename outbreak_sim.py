# 1. Make a network
# 2. Simulate disease spread on the network
# 3. Simulate gradual vaccine uptake 

######################################### IMPORTS #########################################

import numpy as np
import matplotlib.pyplot as plt
import os

import network as nw
import vaccination as vax
import voter_model as vm

################################### AUXILIARY FUNCTIONS ###################################

# function to make a dictionary for any event type
def Event(type, time, primary, secondary):
    # if the event is a transmission...
    if type=='trans':
        event={'type':type,
                'time':time,
                'primary':primary,   # primary is the node that does the infecting
                'secondary':secondary}   # secondary is the node that is infected

    # if the event is a vaccination, 'unvax', "resusceptible" (post-covid immunity wearing off), etc...
    else:
        event={'type':type,
                'time':time,
                'node':primary}   # primary is used to indicate the node (secondary will be passed as None)

    return event


# function to return the next event time
def NewEventTime(time, mu, sigma):
    wait=int((24*60*60)*np.random.lognormal(mu,sigma))   # how long will it be (in seconds) until the next event?
    return time+wait


# function to convert time from seconds to days, hours etc for printing
def ConvertTime(time):
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    return str(day)+" days, "+str(hour)+" hours, "+str(minutes)+" minutes, and "+str(seconds)+" seconds"


# function to calculate lognormal distribution from mode and dispersion
def LogNormal(mode, dispersion):
    sigma=np.log(dispersion)
    mu=(sigma**2)+np.log(mode)
    return abs(sigma), abs(mu)



def main():
    ############################ DEFINE SIMULATION PARAMETERS #############################
    
    # define number of nodes in each age group (proportions from 2019 https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/articles/overviewoftheukpopulation/january2021#the-uks-population-is-ageing)
    totalN = 1000
    N1 = int(0.19*totalN)   # child (aged 0-15) age group
    N2 = int(0.625*totalN)   # adult (aged 16-64) age group
    N3 = int(totalN-(N1+N2))   # elderly (aged 65+) age group

    time_period = (7*24*60*60)   # defines the amount of time to count 'recent' cases (for plotting). default is 1 week

    # selects a determined amount of nodes to be seeds
    seed_no = 5
    patients_zero = np.random.choice(range(0, totalN), size=seed_no)

    # generation times (in days) are drawn from the lognormal distribution defined below...
    g_mode=5 
    g_dispersion=1.3
    g_sigma, g_mu = LogNormal(g_mode, g_dispersion)

    # post-covid immunity times (in days) are drawn from the lognormal distribution defined below...
    c_mode=20
    c_dispersion=c_mode/12
    c_sigma, c_mu = LogNormal(c_mode, c_dispersion)

    # vaccination effectiveness times (in days) are drawn from the lognormal distribution defined below...
    v_mode=20
    v_dispersion=v_mode/12
    v_sigma, v_mu = LogNormal(v_mode, v_dispersion)


    # case severities are drawn from an age-based lognormal distribution defined below...
    R1_sigma = 0.6
    R1_mu = 0.2

    R2_sigma = 0.6
    R2_mu = 0.6

    R3_sigma = 0.5
    R3_mu = 1.1

    av_frac = 0.25   # the fraction of voters who are initialised to be anti-vax

    ################################## SIMULATE NETWORK ##################################

    print("\n-------------- NODE NUMBERS -------------")
    print("Total nodes: " + str(totalN))
    print("U16s: "+str(N1)+", 16-64s: "+str(N2)+", 65+: "+str(N3)+"\n")

    factor = 3   # POLYMOD multiplication factor for daily contacts (to make figures weekly)

    # creates separate disease and behaviour networks (neighbours and bneighbours respectively)
    nodes, neighbours, bneighbours = nw.MakeNetworks(N1, N2, N3, factor)

    # collects the amounts of neighbours that each node has and generates beta value based on R0 (beta * avg. neighbours = R0)
    neighbour_nos = [len(neighbours[i]) for i in neighbours]
    R0=1.3
    beta=R0/np.mean(np.asarray(neighbour_nos))
    

    # nested loops to allow parameters to be changed (for data collection)
    for k in range(1):
        for m in range(52):

            outbreaksizes=[]
            opiniontime = (m+1)*7*24*60*60   # iterates through opinion event timescales week-by-week
            X = 5   # run X iterations of each parameter combination to collect data

            for j in range(X):

                ################################ STATUS ARRAYS ################################

                immune=np.zeros(totalN, dtype=bool)   # an array telling us the immunity of each node (for initial conditions we start with all nodes susceptible)
                active_vax=np.zeros(totalN, dtype=bool)   # an array telling us whether vaccination is active on each node

                opinions = vm.InitBehaviour(totalN, av_frac)   # randomly initialises opinions (zero is anti-vax, 1 is pro-vax)

                severity=np.zeros(totalN)   # an array keeping track of everyone's most severe case of disease
                case_recurrences=np.zeros(totalN)   # an array storing how many cases each node has had



                ######################### CREATING PRE-DETERMINED EVENTS #########################

                tree=[]   # output is a tree-like network
                events=[]   # create a list of events (this list will grow and shrink over time)
                eventslog=[]   # creates a log of all events (this list will only grow)

                # creates seeding events (transmissions at time t=0) and adds to events list
                for i in range(seed_no):
                    events.append(Event('trans', 0, None, patients_zero[i]))

                events.append(Event('kill', 5*365*24*60*60, None, None))   # creates an event to cut the simulation short at 5 years (optional)
                
                #events = vax.RandomVax(vax_frac, totalN, events)   # chooses a given % of nodes to be vaccinated at a random time in the first year
                #events = vax.AgeWaveVax(1, N1, N2, N3, events)   # chooses nodes to be vaccinated in age waves with lognormal time dists (similar to UK COVID vax rollout)
                events = vax.LogDistVax(1, totalN, events)   # chooses random nodes to be vaccinated with lognormal time dists (similar to AgeWaveVax but without waves)

                events = vm.GetOpinionEvents(N1, N2, N3, events, opiniontime)   # fetches each node's initial opinion event (at a random time between t=0 and t=opiniontime)

                active_cases = []   # a list that will store dictionaries of all cases that started in the last week
                case_numbers = []   # a list that will store tuples of active case numbers and times
                active_vax_count = []   # a list that will store tuples of active vaccination numbers and times
                immunity_count = []   # a list that will store tuples of total immune nodes and times

                # counts how many vaccinations and vaccine refusals have occurred
                vax_count = 0
                refuse_count = 0


                ################################## SIMULATE OUTBREAK ##################################

                # start a loop in which we resolve the events in time order until no events remain
                while events:
                    event=min(events,key=lambda x: x['time'])   # fetch earliest infection event on the list
                    events.remove(event)   # remove the chosen infection from the list

                    print("Time: " + str(round(event['time']/(365*24*60*60), 2)) + " years, opinion event timescale: " + str(opiniontime/(24*60*60*7)) + " weeks, iteration " + str(j+1) + "/" + str(X) + "         ", end='\r')   # prints the current working time in years

                    eventslog.append(event)   # permanently stores event in log
                    
                    # if the selected event is a transmission...
                    if event['type']=='trans':
                        # ignoring cases in which the secondary is already immune (so no infection occurs)...
                        if not immune[event['secondary']]:
                            #print("\U0001F534" + str(event['primary'])+' infected '+str(event['secondary'])+' at '+ConvertTime(event['time']))   # print the event
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
                            
                            # updates "most severe case" for node if necessary
                            if case_severity>severity[event['secondary']]:
                                severity[event['secondary']]= case_severity 

                            active_cases.append(event)   # appends the event to the list of active cases
                            case_recurrences[event['secondary']]+=1   # adds a case to the node's total case count

                            # now we need to add more infections to the list...
                            primary=event['secondary']   # "move on" so that the secondary becomes the new primary
                            immune[primary]=True   # make the primary immune so that no future events can affect that node
                            
                            # create new infection events to add to the list
                            for secondary in neighbours[primary]:   # for all neighbours of the primary...
                                if np.random.random()<beta and not immune[secondary]:   # determines if primary infects secondary
                                    transmission_time = NewEventTime(event['time'], g_mu, g_sigma)   # when will the primary infect the secondary?
                                    events.append(Event('trans', transmission_time, primary, secondary))   # creates the transmission event and adds to list

                                    # generates a time for the post-infection immunity to wear off
                                    resusceptible_time = NewEventTime(transmission_time, c_mu, c_sigma)
                                    events.append(Event('resusceptible', resusceptible_time, secondary, None))

                        # if there are no more transmission events in the events list...
                        if len(list(filter(lambda e: e['type'] == 'trans', events)))==0:
                            lastinfection = event['time']   # store the time of the final transmission

                    # if the earliest remaining event is a vaccination...
                    elif event['type']=='vax':
                        if opinions[event['node']] == 1:   # if the node is pro-vax (denoted 1)...
                            immune[event['node']]=True   # makes the node immune
                            active_vax[event['node']]=True   # marks the node as actively vaccinated
                            vax_count+=1   # counts the vaccination
                            #print("\U0001F7E2" + str(event['node']) + " got vaccinated at " + ConvertTime(event['time']))

                        else:
                            refuse_count+=1   # counts the refusal
                            #print("\U0001F535" + str(event['node']) + " refused the vaccine at " + ConvertTime(event['time']))

                        # offers the node another vaccination in a year
                        new_vax_time = event['time'] + (365*24*60*60)
                        events.append(Event('vax', new_vax_time, event['node'], None))

                        # generates a time for post-vaccination immunity to wear off
                        end_time = NewEventTime(event['time'], v_mu, v_sigma)
                        events.append(Event('unvax', end_time, event['node'], None))   # creates 'unvax' event and adds to list

                    elif event['type']=='opinion':
                        opinions[event['node']], changeflag = vm.OpinionEvent(event['node'], bneighbours[event['node']], opinions, severity)   # performs opinion inheritance
                        if changeflag == True:
                            eventslog.append(Event('op_change', event['time'], event['node'], None))   # records the opinion change in the events log

                        events.append(Event('opinion', event['time']+opiniontime, event['node'], None))   # creates the next opinion event for the node

                    elif event['type']=='unvax':
                        immune[event['node']]=False   # node is no longer immune
                        active_vax[event['node']]=False   # vaccination is no longer "active" for this node
                        #print("\U0001F7E0" + str(event['node']) + " became re-susceptible after vaccination at " + ConvertTime(event['time']))

                    elif event['type']=='resusceptible':
                        immune[event['node']]=False   # node is no longer immune
                        #print("\U0001F7E1" + str(event['node']) + " became re-susceptible after infection at " + ConvertTime(event['time']))

                    # when the 'kill' event is reached, delete all future events and finish the simulation
                    elif event['type']=='kill':
                        if len(list(filter(lambda item: item['type'] == 'trans', events)))!=0:
                            lastinfection=event['time']
                        events=[]

                    # removes events from recents if it is older than the specified time_period (typically a week)
                    active_cases = [item for item in active_cases if item['time'] > (event['time']-time_period)]

                    # if there are still active cases, record the time and number of active cases for plotting
                    if len(active_cases)!=0:
                        case_numbers.append((len(active_cases), event['time']))
                        active_vax_count.append((sum(active_vax), event['time']))
                        immunity_count.append((sum(immune), event['time']))

                    # kills the simulation early once there are no more transmissions to be performed
                    if len(list(filter(lambda item: item['type'] == 'trans', events)))==0:
                        events=[]

                    # displays a changing readout of the voter model balance
                    #print("Anti-vax:" + str(sum(i == 0 for i in opinions)) + ", pro-vax: " + str(sum(i == 1 for i in opinions)) + ". Run no. " + str(j+1) + " of " + str(X), end='\r')

                # uses tree to make list of infected nodes
                infected = []
                for x in range(len(tree)):
                    infected.append(tree[x][1])


                ####################### PROCESSING OPINION CHANGE DATA ######################

                all_op_changes = filter(lambda item: item['type'] == 'op_change', eventslog)
                change_timescales = []

                for i in range(totalN):
                    change_list = list(filter(lambda item: item['node'] == i, all_op_changes))
                    if len(change_list) != 0 and len(change_list) != 1:
                        for k in range(len(change_list)-1):
                            change_timescales.append(change_list[k+1]['time']-change_list[k]['time'])

                if len(change_timescales)>0:
                    mean_timescale = round(np.mean(change_timescales))
                else:
                    mean_timescale = None

                ################################ SAVING DATA ################################
                filename = 'opinion_timescales_vs_outbreak_size.csv'
                file = open(filename,'a')
                if os.stat(filename).st_size == 0:
                    file.write("Outbreak size, Delta t between events, Average time between opinion changes, Iteration \n")
                for i in range(1):
                    file.write(str(len(list(filter(lambda item: item['type'] == 'trans', eventslog)))) + "," + str(opiniontime)+"," + str(mean_timescale) + "," + str(j) + "\n")
                file.close()

                outbreaksizes.append(len(list(filter(lambda item: item['type'] == 'trans', eventslog))))

            #filename = 'outbreak_sizes_vs_AV.csv'
            #file = open(filename,'a')
            #if os.stat(filename).st_size == 0:
                #file.write("Outbreak size, Anti-vax fraction, Iteration \n")
            #for i in range(len(outbreaksizes)):
                #file.write(str(outbreaksizes[i]) + "," + str(av_frac)+ "," + str(i) + "\n")
            #file.close()

main()