import numpy as np

def RandomVax(fraction, totalN):
    vax_events=fraction*totalN
    # picking a node to vaccinate....
    picked=np.zeros(totalN, dtype=bool)   # starts with an array of all "false" (unvaccinated)
    for x in range(vax_events):
        pick = random.choice(list(enumerate(picked[picked==False])))   # picks a random unvaccinated node
        picked[pick[0]] = True
        vax_time = np.random.randint(0,31536000)   # picks a random second within the first year to vaccinate
        events.append(Event('vax', vax_time, pick[0], None))   # creates a vax event and adds to the list