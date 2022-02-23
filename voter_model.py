import numpy as np

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


def GetOpinionEvents(N1, N2, N3, events):
    total = N1+N2+N3

    for i in range(total*5):
        choice = np.random.randint(0,total)
        time = np.random.randint(0,365*24*60*60)   # opinion changes can happen for the first year
        events.append(Event('opinion', time, choice))   # creates an opinion event and adds to the list

    return events


def InitBehaviour(N, av_frac):
    opinions = np.zeros(N, dtype=bool)   # an array keeping track of everyone's behaviour status
    for i in range(N):
        roll = np.random.uniform(0.0, 1.0)   # randomly initialises a pro/anti-vax stance for each node
        if roll>=av_frac:
            opinions[i]=1   # ZERO IS ANTI-VAX, ONE IS PRO-VAX

    return opinions


def OpinionEvent(node, neighbours, opinions, severity):
    if len(neighbours)>0:   # clause to avoid breaking on nodes with no neighbours
        neighbourpick = np.random.choice(neighbours[node])   # chooses a random neighbour

        change_prob = 1.0   # probability of taking neighbours opinion is 1 by default

        # if the potential opinion change is from pro-vax to anti-vax, check extra conditions...
        if opinions[neighbourpick]==False and opinions[node]==True:
            checker=False

            # checks if any neighbours had a "severe" case (above 0.8)
            for i in range(len(neighbours)):
                if severity[neighbours[i]]>0.8:
                    checker=True
            # checks if the node itself has had a "severe" case (above 0.8)
            if severity[node]>=0.8:
                checker=True

            # if the node or its neighbours have had a severe case, reduce change probability by 80%
            if checker==True:
                change_prob = change_prob - 0.8

        # adopts neighbour's behaviour with the change probability
        roll = np.random.uniform(0.0, 1.0)
        if roll < change_prob:
            opinions[node] = opinions[neighbourpick]

        return opinions[node]

    else:
        return opinions[node]