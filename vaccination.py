import numpy as np
import random


def Event(type, time, node):
    # each event is a small dictionary with keys...
            # type: the type of event which occurs
            # time: the time that the event occurs 
            # primary: the node that is doing the infecting
            # secondary: the node that is being infected

    event={'type':type,
            'time':time,
            'node':node}

    return event


# function to return the next event time
def NewEventTime(time, mu, sigma):
    wait=int((24*60*60)*np.random.lognormal(mu,sigma))   # how long will it be (in seconds) until the next event?
    return time+wait


# this was the default vaccination method used in outbreak_sim.py before 21/12
def RandomVax(fraction, totalN, events):
    vaxevents_no=int(fraction*totalN)
    picked=np.zeros(totalN, dtype=bool)   # starts with an array of all "false" (unvaccinated)

    # picking nodes to vaccinate....
    for x in range(vaxevents_no):
        pick = random.choice(list(enumerate(picked[picked==False])))   # picks a random unvaccinated node
        picked[pick[0]] = True
        vax_time = np.random.randint(0,31536000)   # picks a random second within the first year to vaccinate
        events.append(Event('vax', vax_time, pick[0]))   # creates a vax event and adds to the list

    return events


# ------ AGE WAVE VAX NOTES ------
# This method can offer staggered vaccination to the three rings of nodes, which is meant to simulate age-based vax rollout.
# There is also a condensed version of this (LogDistVax), which is the same but all rings use the same timescale (no waves).

def AgeWaveVax(frac, N1, N2, N3, events):
    picked1=np.zeros(N1, dtype=bool)   # starts with an array of all "false" children (not offered vaccination)
    picked2=np.zeros(N2, dtype=bool)   # starts with an array of all "false" adults (not offered vaccination)
    picked3=np.zeros(N3, dtype=bool)   # starts with an array of all "false" elderly (not offered vaccination)

    # creates an appropriate shape compared to data (used https://www.medcalc.org/manual/log-normal-distribution-functions.php to visualise)
    N3_sigma = 1
    N3_mu = 4.5

    # picking ring 3 (elderly) nodes to vaccinate first...
    for x in range(int(frac*N3)):
        pick = random.choice(list(enumerate(picked3[picked3==False])))   # pick a random elderly node
        picked3[pick[0]] = True   # mark the node as chosen

        picked3[pick[0]] = True

        vax_time = NewEventTime(0, N3_mu, N3_sigma)   # picks a random second within the first year to vaccinate
        vax_time = vax_time + (330*24*60*60)   # first (elderly) vaccine in the uk was after 11 months - this is a correction to delay all vaccines

        events.append(Event('vax', vax_time, pick[0]))   # creates a vax event and adds to the list

    
    # picking ring 2 (adult) nodes to vaccinate next...
    for x in range(int(frac*N2)):
        pick = random.choice(list(enumerate(picked2[picked2==False])))   # pick a random adult node
        picked2[pick[0]] = True   # mark the node as chosen

        vax_time = NewEventTime(0, N3_mu, N3_sigma)   # picks a random second within the first year to vaccinate
        vax_time = vax_time + (400*24*60*60)   # delays adult vaccination by ~13 months (2 months after elderly vax begins)

        events.append(Event('vax', vax_time, pick[0]))   # creates a vax event and adds to the list


    # lowers the fraction significantly to reflect low vax rate in children
    frac = 0.05

    # picking ring 1 (child) nodes to vaccinate last...
    for x in range(int(frac*N1)):
        pick = random.choice(list(enumerate(picked1[picked1==False])))   # pick a random youth node
        picked1[pick[0]] = True   # mark the node as chosen

        vax_time = NewEventTime(0, N3_mu, N3_sigma)   # picks a random second within the first year to vaccinate
        vax_time = vax_time + (450*24*60*60)   # delays youth vaccination by ~15 months (2 months after adult vax begins)

        events.append(Event('vax', vax_time, pick[0]))   # creates a vax event and adds to the list

    return events



# ------ LOG DIST VAX NOTES ------
# This method can offers vaccination to all three rings of nodes simultaneously (no age-based waves).
# This is a simplified version of AgeBasedVax.

def LogDistVax(frac, N, events):
    picked=np.zeros(N, dtype=bool)   # starts with an array of all "false" nodes (not offered vaccination)

    # creates an appropriate shape compared to data (used https://www.medcalc.org/manual/log-normal-distribution-functions.php to visualise)
    N_sigma = 1
    N_mu = 5

    # picking nodes to offer vaccination...
    for x in range(int(frac*N)):
        pick = random.choice(list(enumerate(picked[picked==False])))   # pick a random node
        picked[pick[0]] = True   # mark the node as chosen

        # picks a vaccination time after 40 days
        vax_time = NewEventTime(0, N_mu, N_sigma)   # picks a random second to offer vaccination
        vax_time = vax_time + (40*24*60*60)   # delay vaccination to start at 40 days

        events.append(Event('vax', vax_time, pick[0]))   # creates a vax event and adds to the list

    return events