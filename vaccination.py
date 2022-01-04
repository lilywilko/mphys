import numpy as np
import random


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


# this was the default vaccination method used in outbreak_sim.py before 21/12
def RandomVax(fraction, totalN, events):
    vaxevents_no=int(fraction*totalN)
    picked=np.zeros(totalN, dtype=bool)   # starts with an array of all "false" (unvaccinated)

    # picking nodes to vaccinate....
    for x in range(vaxevents_no):
        pick = random.choice(list(enumerate(picked[picked==False])))   # picks a random unvaccinated node
        picked[pick[0]] = True
        vax_time = np.random.randint(0,31536000)   # picks a random second within the first year to vaccinate
        events.append(Event('vax', vax_time, pick[0], None))   # creates a vax event and adds to the list

    return events


def AgeWaveVax(N1frac, N2frac, N3frac, N1, N2, N3):
    picked=np.zeros(N1+N2+N3, dtype=bool)   # starts with an array of all "false" (unvaccinated)

    # real time from first UK case to first UK vaccination (for 65+) was ~11 months
    N3_mode = 100
    N3_dispersion = 60
    N3_sigma, N3_mu = LogNormal(N3_mode, N3_dispersion)

    # picking ring 3 nodes to vaccinate first...
    for x in range(int(N3frac*N3)):
        pick = 0
        while pick < N1+N2:
            pick = random.choice(list(enumerate(picked[picked==False])))   # keeps picking until the pick is in ring 3
        picked[pick[0]] = True
        vax_time = NewEventTime(0, N3_mu, N3_sigma)   # picks a random second within the first year to vaccinate
        events.append(Event('vax', vax_time, pick[0], None))   # creates a vax event and adds to the list