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


def GetOpinionEvents(N1, N2, N3, events, timescale):
    total = N1+N2+N3
    picked=np.zeros(total, dtype=bool)   # starts with an array of all "false" (unvaccinated)

    for i in range(total):
        pick = random.choice(list(enumerate(picked[picked==False])))
        time = np.random.randint(0,timescale)   # initial opinion change is randomly performed within the first time period
        events.append(Event('opinion', time, pick[0]))   # creates an opinion event and adds to the list
        picked[pick[0]]=True

    return events


def InitBehaviour(N, av_frac):
    opinions = np.zeros(N, dtype=bool)   # an array keeping track of everyone's behaviour status
    for i in range(N):
        roll = np.random.uniform(0.0, 1.0)   # randomly initialises a pro/anti-vax stance for each node
        if roll>=av_frac:
            opinions[i]=1   # ZERO IS ANTI-VAX, ONE IS PRO-VAX

    return opinions


def OpinionEvent(node, neighbours, opinions, severity):
    changeflag = False   # introduces a flag to check whether node opinion flips

    if len(neighbours)>0:   # clause to avoid breaking on nodes with no neighbours
        neighbourpick = np.random.choice(neighbours)   # chooses a random neighbour

        change_prob = 1.0   # probability of taking neighbours opinion is 1 by default

        # if the potential opinion change is from pro-vax to anti-vax, check extra conditions...
        if opinions[neighbourpick]==False and opinions[node]==True:
            neighbourchecker=False
            selfchecker=False

            # checks if any neighbours had a "severe" case (above 0.8)
            for i in range(len(neighbours)):
                if severity[neighbours[i]]>=0.8:
                    neighbourchecker=True
            # checks if the node itself has had a "severe" case (above 0.8)
            if severity[node]>=0.8:
                selfchecker=True

            # if neighbours have had a severe case, reduce change probability by 50%
            if neighbourchecker==True:
                change_prob = change_prob - 0.5

            # if the node itself has had a severe case, reduce change probability by 50%
            if selfchecker==True:
                change_prob = change_prob - 0.5

        # adopts neighbour's behaviour with the change probability
        roll = np.random.uniform(0.0, 1.0)
        if roll < change_prob:
            if opinions[node] != opinions[neighbourpick]:
                changeflag=True
            opinions[node] = opinions[neighbourpick]

        return opinions[node], changeflag

    else:
        return opinions[node], changeflag