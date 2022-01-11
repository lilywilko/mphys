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
        time = np.random.randint(0,31536000*12)   # opinion changes can happen for the first twelve years
        events.append(Event('opinion', time, choice))   # creates an opinion event and adds to the list

    return events