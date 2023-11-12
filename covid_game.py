# 1. Make a network
# 2. Simulate disease spread on the network
# 3. Simulate gradual vaccine uptake 

######################################### IMPORTS #########################################

import time
import numpy as np
from modules import network as nw
from modules import vaccination as vax
from modules import voter_model as vm

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


# colours the text output of node numbers (for list mode outputs)
def NodeColour(node, N1, N2, N3):
    if node == '?':
        return node
    elif int(node)<N1:
        return "\033[91m"+str(node)+"\033[0m"   # if the node is a child, colour the text red
    elif int(node)<N2:
        return "\033[93m"+str(node)+"\033[0m"   # if the node is an adult, colour the text yellow
    else:
        return "\033[92m"+str(node)+"\033[0m"   # if the node is elderly, colour the text green


# function to return the next event time
def NewEventTime(time, mu, sigma):
    wait=int((24*60*60)*np.random.lognormal(mu,sigma))   # how long will it be (in seconds) until the next event?
    return time+wait


# function to convert time from seconds to days, hours, minutes and seconds for printing to user
def ConvertTime(time):
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    return str(round(day))+" days, "+str(round(hour))+" hours, "+str(round(minutes))+" mins, and "+str(round(seconds))+" secs", day+1


# function to calculate lognormal distribution from mode and dispersion
def LogNormal(mode, dispersion):
    sigma=np.log(dispersion)
    mu=(sigma**2)+np.log(mode)
    return abs(sigma), abs(mu)



def main():
    ##################################### INTRODUCTORY PRINTOUTS #####################################
    # Introductory text, welcoming the user and describing the simulation
    print("")
    print("--------------------------------------------------------------------------")
    print("----------------\U0001f9a0 Welcome to the COVID-19 simulation! \U0001f9a0-----------------")
    print("--------------------------------------------------------------------------")
    print("")
    print("In this program, you will simulate how COVID-19 spreads between 1000\npeople who have contact with each other in a network.")
    print("")
    print("People in the simulation can choose to get vaccinated, but can also\nrefuse a vaccine if they wish. They inherit their opinion on vaccination\nfrom friends and family.")
    print("")
    print("You can choose the parameters of the simulation, including:")
    print("   \U0001F46A how many of the people are children, adults, and elderly people")
    print("   \U0001F489 how many are initially anti-vaccination (this will change over time)")
    print("   \u23F0 how long vaccination protects people for.")
    print("")
    print("For help and more information, see the Instruction Manual.")
    print("")

    # waits for user to begin the program
    while True:
            begin = str(input("Are you ready to begin? (Y/N): "))
            if begin in ("y","Y","yes","Yes"):
                break
            else:
                print("Please try again...")
    print("")

    continue_code=True   # closes program (by breaking out of run loop) once the user decides not to continue
    # enters repeatable part of the simulation (defining parameters and running outbreak)
    while continue_code==True:

        ##################################### CHOOSING PARAMETERS #####################################

        print("\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0")
        print("")
        print("-----------------\U0001f9a0 Choosing simulation parameters... \U0001f9a0------------------")
        print("")

        totalN = 1000   # number of nodes is always 1000



        # gets user input for the age distribution
        print("\U0001F4CA The \033[92mdefault age distribution\033[0m in this simulation is the same as the UK\npopulation: 19% children (0-15), 62.5% adults (16-64) and 18.5% elderly\npeople (65+).")
        while True:
            choice = str(input("Would you like to use a custom mix of ages instead? (Y/N): "))
            if choice in ("y","Y","yes","Yes","n","N","no","No"):
                break
            else:
                print("Your input was not valid! Please try again...")

        # default age distribution is the UK population distribution
        if choice in ("n","N","no","No"):
            N1 = int(0.19*totalN)   # child (aged 0-15) age group
            N2 = int(0.625*totalN)   # adult (aged 16-64) age group
            N3 = int(totalN-(N1+N2))   # elderly (aged 65+) age group
        
        # if they wish to use custom mix, get three percentages from them (must add to 100)
        else:
            print("")
            print("\u2755 Note: your next three inputs must add up to 100.")
            c_trigger = False   # triggers a second input attempt if the first fails
            a_trigger = False   # triggers a second input attempt if the first fails
            e_trigger = False   # triggers a second input attempt if the first fails

            c_number = 101
            while c_number > 100:
                if c_trigger == True:
                    print("The number you enter must be between 0 and 100!\nPlease try again...")
                try:
                    c_number = float(input("Enter the percentage who will be children (without the %): "))
                    c_trigger = True
                except:
                    print("\nThat is not a number! Please try again...")
                    c_number = float(input("Enter the percentage who will be children (without the %): "))
            N1 = int((c_number/100)*totalN)

            a_number = 101
            while a_number > (100-c_number):
                if a_trigger == True:
                    print("The number you enter must be between 0 and (100 - % that are children)!\nPlease try again...")
                try:
                    a_number = float(input("Enter the percentage who will be adults (without the %): "))
                    a_trigger = True
                except:
                    print("\nThat is not a number! Please try again...")
                    a_number = float(input("Enter the percentage who will be adults (without the %): "))
            N2 = int((a_number/100)*totalN)

            e_number = 101
            while e_number != (100-(c_number+a_number)):
                if e_trigger == True:
                    print("The number must be between 0 and (100 - % that are children and adults)!\nPlease try again...")
                try:
                    e_number = float(input("Enter the percentage who will be elderly (without the %): "))
                    e_trigger = True
                except:
                    print("\nThat is not a number! Please try again...")
                    e_number = float(input("Enter the percentage who will be elderly (without the %): "))
            N3 = int((e_number/100)*totalN)



        # gets user input for the percentage that are anti-vax
        print("")
        print("\U0001F489 The \033[92mdefault amount of people who are anti-vaccination\033[0m at the start of\nthe simulation is 25%.")

        while True:
            choice = str(input("Would you like to use a custom percentage instead? (Y/N): "))
            if choice in ("y","Y","yes","Yes","n","N","no","No"):
                break
            else:
                print("Your input was not valid! Please try again...")

        # default anti-vax percentage is 25%
        if choice in ("n","N","no","No"):
            av_frac = 0.25   # the fraction of voters who are initialised to be anti-vax

        # if they wish to use a custom number, get their input
        else:
            av_frac = 101
            av_trigger=False   # triggers a second input attempt if the first fails
            while av_frac > 100:
                if av_trigger == True:
                    print("The number you enter must be between 0 and 100!\nPlease try again...")
                try:
                    av_frac = float(input("Enter the percentage who will be anti-vaccination (without the %): "))
                    av_trigger = True
                except:
                    print("\nThat is not a number! Please try again...")
                    av_frac = float(input("Enter the percentage who will be anti-vaccination (without the %): "))
            av_frac=av_frac/100
        


        # gets user input for the vax effectiveness time
        print("")
        print("\u231B The \033[92mdefault average time that vaccination is effective for\033[0m is 90 days.")

        while True:
            choice = str(input("Would you like to use a custom time period instead? (Y/N): "))
            if choice in ("y","Y","yes","Yes","n","N","no","No"):
                break
            else:
                print("Your input was not valid! Please try again...")

        # default effectiveness time is 90 days
        if choice in ("n","N","no","No"):
            v_mode=90

        # otherwise, get their input
        else:
            v_mode = -1
            vax_trigger=False   # triggers a second input attempt if the first fails
            while v_mode < 0:
                if vax_trigger == True:
                    print("The number you enter must be 0 or higher!\nPlease try again...")
                try:
                    v_mode = float(input("Enter the amount of time in days that the vaccine will work for: "))
                    vax_trigger = True
                except:
                    print("\nThat is not a number! Please try again...")
                    v_mode = float(input("Enter the amount of time in days that the vaccine will work for: "))



        # gets user input for the pause before vaccination kicks in
        print("")
        print("\u231B By default, the \033[92mvaccination scheme begins\033[0m after 40 days.")

        while True:
            choice = str(input("Would you like to use a custom wait period (or none) instead? (Y/N): "))
            if choice in ("y","Y","yes","Yes","n","N","no","No"):
                break
            else:
                print("Your input was not valid! Please try again...")

        # by default, the wait is 40 days
        if choice in ("n","N","no","No"):
            # vaccination effectiveness times (in days) are drawn from the lognormal distribution defined below...
            vax_wait = 40

        # otherwise, get their input
        else:
            vax_wait = -1
            wait_trigger=False   # triggers a second input attempt if the first fails
            while vax_wait < 0:
                if wait_trigger == True:
                    print("The number you enter must be 0 or higher!\nPlease try again...")
                try:
                    vax_wait = float(input("Enter the amount of time in days before people can be vaccinated: "))
                    wait_trigger = True
                except:
                    print("\nThat is not a number! Please try again...")
                    vax_wait = float(input("Enter the amount of time in days before people can be vaccinated: "))

        # calculates dispersion, sigma and mu based on their input/the default
        v_dispersion=v_mode/12
        v_sigma, v_mu = LogNormal(v_mode, v_dispersion)



        # gets user input of number of patient zeros
        print("")
        print("\U0001F637 The \033[92mdefault number of 'patient zeros'\033[0m (people with COVID at the very\nbeginning of the simulation) is 5.")

        while True:
            choice = str(input("Would you like to include a different emount of patient zeros? (Y/N): "))
            if choice in ("y","Y","yes","Yes","n","N","no","No"):
                break
            else:
                print("Your input was not valid! Please try again...")

        # default is five (to limit the amount of false start simulations)
        if choice in ("n","N","no","No"):
            seed_no = 5

        # otherwise get their input
        else:
            seed_no = -1
            p0_trigger=False   # triggers a second input attempt if the first fails
            while seed_no < 0 or seed_no>totalN:
                if p0_trigger == True:
                    print("The number you enter must be between 0 and 1000!\nPlease try again...")
                try:
                    seed_no = int(input("Enter the amount of patient zeros: "))
                    p0_trigger = True
                except:
                    print("\nThat is not a valid number! Please try again...")
                    seed_no = int(input("Enter the amount of patient zeros: "))


        ##################################### OUTPUT SETTINGS #####################################
        print("")
        print("\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0")
        print("")
        print("------------------------\U0001f9a0 Output settings... \U0001f9a0--------------------------")
        print("")
        print("\U0001F4CB You can view the simulation results as a list or table that updates\nin real time.")


        # asks whether they want to see a list or a table
        while True:
            choice = str(input("Enter L for a list or T for a table: "))
            if choice in ("t","T","table","Table","l","L","list","List"):
                break
            else:
                print("Your input was not valid! Please try again...")

        print("")
        print("\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0-\U0001f9a0")
        print("")

        if choice in ("l","L","list","List"):   # for a list, print the colour guide
            output_type = "list"
            print("")
            print("U16s are labelled \033[91m0-"+str(N1)+"\033[0m. 16-64s are labelled \033[93m"+str(N1)+"-" + str(N1+N2)+ "\033[0m. 65+ are labelled\n\033[92m"+str(N1+N2)+"-"+str(N1+N2+N3)+"\033[0m.\n")
        else:
            output_type = "table"


        ##################################### PRE-DETERMINED PARAMETERS #####################################

        time_period = (7*24*60*60)   # defines the amount of time to count 'recent' cases. default for COVID-19 is 1 week

        # generation times (in days) are drawn from the lognormal distribution defined below...
        g_mode=5 
        g_dispersion=1.3
        g_sigma, g_mu = LogNormal(g_mode, g_dispersion)

        # post-covid immunity times (in days) are drawn from the lognormal distribution defined below...
        c_mode=90
        c_dispersion=8
        c_sigma, c_mu = LogNormal(c_mode, c_dispersion)

        # case severities are drawn from an age-based lognormal distribution defined below...
        R1_sigma = 0.6
        R1_mu = 0.2

        R2_sigma = 0.6
        R2_mu = 0.6

        R3_sigma = 0.5
        R3_mu = 1.1

        factor = 3   # POLYMOD multiplication factor for daily contacts (to make figures weekly)


        ##################################### MAKE NETWORK #####################################

        # creates separate disease and behaviour networks (neighbours and bneighbours respectively)
        nodes, neighbours, bneighbours = nw.MakeNetworks(N1, N2, N3, factor)

        # collects the amounts of neighbours that each node has and generates beta value based on R0 (beta * avg. neighbours = R0)
        neighbour_nos = [len(neighbours[i]) for i in neighbours]
        R0=1.4
        beta=R0/np.mean(np.asarray(neighbour_nos))
        opiniontime = 6*7*24*60*60   # iterates through opinion event timescales week-by-week

        ##################################### STATUS ARRAYS #####################################

        patients_zero = np.random.choice(range(0, totalN), size=seed_no)   # chooses patient zeros
        immune=np.zeros(totalN, dtype=bool)   # an array telling us the immunity of each node (for initial conditions we start with all nodes susceptible)
        active_vax=np.zeros(totalN, dtype=bool)   # an array telling us whether vaccination is active on each node

        opinions = vm.InitBehaviour(totalN, av_frac)   # randomly initialises opinions (zero is anti-vax, 1 is pro-vax)

        severity=np.zeros(totalN)   # an array keeping track of everyone's most severe case of disease

        active_cases = []   # a list that will store dictionaries of all cases that started in the last week
        case_numbers = []   # a list that will store tuples of active case numbers and times
        active_vax_count = []   # a list that will store tuples of active vaccination numbers and times
        immunity_count = []   # a list that will store tuples of total immune nodes and times

        # counts how many vaccinations and vaccine refusals have occurred
        vax_count = 0
        refuse_count = 0


        ##################################### CREATING PRE-DETERMINED EVENTS #####################################

        events=[]   # create a list of events (this list will grow and shrink over time)
        eventslog=[]   # creates a log of all events (this list will only grow)

        # creates seeding events (transmissions at time t=0) and adds to events list
        for i in range(seed_no):
            print("Patient zero " + NodeColour(patients_zero[i], N1, N2, N3) + " has contact with " + str(len(neighbours[patients_zero[i]])) + " people while they have COVID-19.")   # prints the neighbours of each patient zero to the user
            events.append(Event('trans', 0, "?", patients_zero[i]))

        events.append(Event('kill', 2*365*24*60*60, None, None))   # creates an event to cut the simulation short at 2 years
        events = vax.RandomVax(totalN, events, vax_wait)   # offers a first vaccination to every node at a random time in the first year
        events = vm.GetOpinionEvents(N1, N2, N3, events, opiniontime)   # fetches each node's initial opinion event (at a random time between t=0 and t=opiniontime)
        

        ##################################### BEGIN SIMULATION #####################################

        print("")
        print("---------------------------\U0001f9a0 Let's begin! \U0001f9a0-----------------------------")

        time.sleep(2)   # pause for the user to read the text above!

        if output_type=='table':   # print the table header
            print("--------------------------------------------------------------------------")
            print("Time           Total cases     Active cases    Vaccinations     Refusals      ")
            print("--------------------------------------------------------------------------")


        # start a loop in which we resolve the events in time order until no events remain
        while events:
            event=min(events,key=lambda x: x['time'])   # fetch earliest infection event on the list
            events.remove(event)   # remove the chosen infection from the list
            eventslog.append(event)   # permanently stores event in log
            
            # if the selected event is a transmission...
            if event['type']=='trans':
                # ignoring cases in which the secondary is already immune (so no infection occurs)...
                if not immune[event['secondary']]:
                    if output_type == 'list':
                        print("\U0001F9A0 " + NodeColour(event['primary'], N1, N2, N3)+' infected '+ NodeColour(event['secondary'], N1, N2, N3)+' at '+ConvertTime(event['time'])[0])   # print the event
                    else:
                        print('%-15s%-15s%-15s%-15s%-14s' % ("Day "+str(ConvertTime(event['time'])[1]),"\U0001F9A0 "+str(len(list(filter(lambda item: item['type'] == 'trans', eventslog)))), "\U0001F4C8 " + str(len(active_cases)), "\U0001F489 "+str(vax_count), "\U0001F645 "+str(refuse_count)), flush=True)

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
                    if output_type == 'list':
                        print("\U0001F489 " + NodeColour(event['node'], N1, N2, N3) + " got vaccinated at " + ConvertTime(event['time'])[0])
                    else:
                        print('%-15s%-15s%-15s%-15s%-14s' % ("Day "+str(ConvertTime(event['time'])[1]),"\U0001F9A0 "+str(len(list(filter(lambda item: item['type'] == 'trans', eventslog)))), "\U0001F4C8 " + str(len(active_cases)), "\U0001F489 "+str(vax_count), "\U0001F645 "+str(refuse_count)), flush=True)

                else:
                    refuse_count+=1   # counts the refusal
                    if output_type == 'list':
                        print("\U0001F645 " + NodeColour(event['node'], N1, N2, N3) + " refused the vaccine at " + ConvertTime(event['time'])[0])
                    else:
                        print('%-15s%-15s%-15s%-15s%-14s' % ("Day "+str(ConvertTime(event['time'])[1]),"\U0001F9A0 "+str(len(list(filter(lambda item: item['type'] == 'trans', eventslog)))), "\U0001F4C8 " + str(len(active_cases)), "\U0001F489 "+str(vax_count), "\U0001F645 "+str(refuse_count)), flush=True)

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

            elif event['type']=='resusceptible':
                immune[event['node']]=False   # node is no longer immune

            # when the 'kill' event is reached, delete all future events and finish the simulation
            elif event['type']=='kill':
                if len(list(filter(lambda item: item['type'] == 'trans', events)))!=0:
                    lastinfection=event['time']
                events=[]
                print("")
                print("This COVID-19 outbreak lasted longer than two years and likely became \033[1m\033[91mendemic\033[0m\033[0m, meaning that it stayed in the population in the long term (like the flu).")   # tell the user that the outbreak was endemic

            # removes events from recents if it is older than the specified time_period (typically a week)
            active_cases = [item for item in active_cases if item['time'] > (event['time']-time_period)]

            # kills the simulation early once there are no more transmissions to be performed
            if len(list(filter(lambda item: item['type'] == 'trans', events)))==0:
                events=[]
                print("")
                print("This outbreak ended after " + str(ConvertTime(event['time'])[1]) + " days because \033[1m\033[92mnobody else was infected.\033[0m\033[0m")   # tells the user that the outbreak ended early


        print("")
        # asks user whether they would like to execute another epidemic run
        while True:
            choice = str(input("Run another epidemic? (Y/N): "))
            if choice in ("y","Y","yes","Yes","n","N","no","No","quit","exit"):
                break
            else:
                print("You typed something wrong! Please try again...")

        # quits code if the user does not wish to continue
        if choice in ("n","N","no","No","quit","exit"):
            continue_code=False
            print("")
            print("Thank you for using the simulation!")
            print("Goodbye! \U0001F44B")
            print("")
main()