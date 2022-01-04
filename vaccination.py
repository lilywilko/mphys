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
        events.append(Event('vax', vax_time, pick[0], None))   # creates a vax event and adds to the list

    return events


def AgeWaveVax(frac, N1, N2, N3, events):
    picked1=np.zeros(N1, dtype=bool)   # starts with an array of all "false" (unvaccinated) children
    picked2=np.zeros(N2, dtype=bool)   # starts with an array of all "false" (unvaccinated) adults
    picked3=np.zeros(N3, dtype=bool)   # starts with an array of all "false" (unvaccinated) elderly

    # creates an appropriate shape compared to data (used https://www.medcalc.org/manual/log-normal-distribution-functions.php to visualise)
    N3_sigma = 1
    N3_mu = 4.5

    # picking ring 3 (elderly) nodes to vaccinate first...
    for x in range(int(frac*N3)):
        pick = random.choice(list(enumerate(picked3[picked3==False])))

        picked3[pick[0]] = True

        vax_time = NewEventTime(0, N3_mu, N3_sigma)   # picks a random second within the first year to vaccinate
        vax_time = vax_time + (330*24*60*60)   # first vaccine in the uk was after 11 months - this is a correction to delay all vaccines

        events.append(Event('vax', vax_time, pick[0], None))   # creates a vax event and adds to the list

        print("Choosing elderly people to vaccinate..." + str(x), end="\r")

    
    # picking ring 2 (adult) nodes to vaccinate next...
    for x in range(int(frac*N2)):
        pick = random.choice(list(enumerate(picked2[picked2==False])))

        picked2[pick[0]] = True

        vax_time = NewEventTime(0, N3_mu, N3_sigma)   # picks a random second within the first year to vaccinate
        vax_time = vax_time + (450*24*60*60)   # first vaccine in the uk was after 11 months - this is a correction to delay all vaccines

        events.append(Event('vax', vax_time, pick[0], None))   # creates a vax event and adds to the list

        print("Choosing adults to vaccinate..." + str(x), end="\r")


    # lowers the fraction significantly as not many children have been vaccinated
    frac = 0.05

    # picking ring 1 (child) nodes to vaccinate last...
    for x in range(int(frac*N1)):
        pick = random.choice(list(enumerate(picked1[picked1==False])))

        picked1[pick[0]] = True

        vax_time = NewEventTime(0, N3_mu, N3_sigma)   # picks a random second within the first year to vaccinate
        vax_time = vax_time + (450*24*60*60)   # first vaccine in the uk was after 11 months - this is a correction to delay all vaccines

        events.append(Event('vax', vax_time, pick[0], None))   # creates a vax event and adds to the list

        print("Choosing children to vaccinate...", str(x), end="\r")

    return events