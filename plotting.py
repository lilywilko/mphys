import numpy as np
import csv
import matplotlib.pyplot as plt

# function to plot the distribution of outbreak sizes
def VariableVax(values, n):
    colours = ['#f5e160', None, '#ffa556', None, '#ed7068', None, '#be4b7a', None, '#8d1e9f', None, '#13316f']
    for i in range(11):
        plotting=[]
        for j in range(len(values)):
            if values[j][0]==(i*10) and values[j][1]>14:
                plotting.append(values[j][1])
        
        # plot every other histogram to make graph less busy
        if i%2==0:
            plt.hist(plotting, bins=20, label=str(i*10)+"% vax", histtype='step', color=colours[i])   # draws histogram of outbreak sizes

    plt.xlabel("Outbreak size")
    plt.ylabel("Frequency")
    plt.title("Distribution of outbreak sizes for "+str(int(len(values)/11))+" simulated outbreaks \n on a network of "+str(n)+" nodes, with outbreaks under 15 emitted")
    plt.legend()
    plt.show()


def ActiveCases(cases, times, label):
    plt.xlabel("Time (days)")
    plt.ylabel("Active cases")
    plt.title("Number of active cases vs. time for a network of 10,000 people")
    plt.plot(times, cases, ".", markersize=1, label=label)


def GetACData(filename):
    cases = []
    times = []

    with open(filename) as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader, None)
        for row in csv_reader:
            cases.append(int(row[0]))
            times.append(int(row[1]))

    times = np.array(times)
    times = times/(60*60*24)   # converts time to days for readability

    return cases, times


def GetSWLData(filename, percent):
    cases = []
    times = []

    with open(filename) as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader, None)
        for row in csv_reader:
            if float(row[2])==percent:
                cases.append(int(row[0]))
                times.append(int(row[1]))

    times = np.array(times)
    times = times/(60*60*24)   # converts time to days for readability

    return cases, times


def main():
    plt.style.use('seaborn-colorblind')
    # ---------------- PLOTTING FOR VARIABLE VACCINATION RATES ----------------
    #values = []
    #with open('5000_outbreaks_vs_vax_percentage.csv') as file:
        #csv_reader = csv.reader(file, delimiter=',')
        #next(csv_reader, None)
        #for row in csv_reader:
            #values.append((int(row[10]), int(row[11])))
        #n=row[0]
    #VariableVax(values,n)

    # ------------- PLOTTING FOR ACTIVE CASES OVER TIME (ORIGINAL) ------------

    #cases1, times1 = GetACData('fix_active_cases_data.csv')
    #cases2, times2 = GetACData('fix_active_cases_data_2.csv')
    #cases3, times3 = GetACData('fix_active_cases_data_3.csv')
    #cases4, times4 = GetACData('fix_active_cases_data_4.csv')
    #cases5, times5 = GetACData('fix_active_cases_data_5.csv')
    #cases6, times6 = GetACData('fix_active_cases_data_6.csv')
    #cases7, times7 = GetACData('fix_active_cases_data_7.csv')
    #cases8, times8 = GetACData('fix_active_cases_data_8.csv')
    #cases9, times9 = GetACData('fix_active_cases_data_9.csv')
    #cases10, times10 = GetACData('fix_active_cases_data_10.csv')

    #ActiveCases(cases1, times1, None)
    #ActiveCases(cases2, times2, None)
    #ActiveCases(cases3, times3, None)
    #ActiveCases(cases4, times4, None)
    #ActiveCases(cases5, times5, None)
    #ActiveCases(cases6, times6, None)
    #ActiveCases(cases7, times7, None)
    #ActiveCases(cases8, times8, None)
    #ActiveCases(cases9, times9, None)
    #ActiveCases(cases10, times10, None)

    # -------------------- PLOTTING ACTIVE CASES VS. BETA -------------------
    #cases1, times1 = GetACData('beta_0.8_cases_data.csv')
    #cases2, times2 = GetACData('beta_0.5_cases_data.csv')
    #cases3, times3 = GetACData('beta_0.4_cases_data.csv')
    #cases4, times4 = GetACData('beta_0.3_cases_data.csv')
    #cases5, times5 = GetACData('beta_0.25_cases_data.csv')

    #ActiveCases(cases1, times1, "Beta = 0.8")
    #ActiveCases(cases2, times2, "Beta = 0.5")
    #ActiveCases(cases3, times3, "Beta = 0.4")
    #ActiveCases(cases4, times4, "Beta = 0.3")
    #ActiveCases(cases5, times5, "Beta = 0.25")

    # --------------- PLOTTING ACTIVE CASES VS. SWL PERCENTAGE --------------
    #cases1, times1 = GetSWLData("variable_SWL_cases_data.csv", 0.1)
    #cases2, times2 = GetSWLData("variable_SWL_cases_data.csv", 0.2)
    #cases3, times3 = GetSWLData("variable_SWL_cases_data.csv", 0.3)
    #cases4, times4 = GetSWLData("variable_SWL_cases_data.csv", 0.4)
    #cases5, times5 = GetSWLData("variable_SWL_cases_data.csv", 0.5)
    #cases6, times6 = GetSWLData("variable_SWL_cases_data.csv", 0.6)
    #cases7, times7 = GetSWLData("variable_SWL_cases_data.csv", 0.7)

    #ActiveCases(cases1, times1, "10% of N per ring")
    #ActiveCases(cases2, times2, "20% of N per ring")
    #ActiveCases(cases3, times3, "30% of N per ring")
    #ActiveCases(cases4, times4, "40% of N per ring")
    #ActiveCases(cases5, times5, "50% of N per ring")
    #ActiveCases(cases6, times6, "60% of N per ring")
    #ActiveCases(cases7, times7, "70% of N per ring")

    # --------------- PLOTTING VACCINATION UPTAKE VS REFUSAL ---------------

    uptakes = []
    refusals = []
    times = []

    with open('vaccinations_vs_refusals.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader, None)
        for row in csv_reader:
            uptakes.append(int(row[0]))
            refusals.append(int(row[1]))
            times.append(int(row[2]))

    totals = np.asarray(uptakes) + np.asarray(refusals)

    times = np.array(times)
    times = times/(60*60*24)   # converts time to days for readability

    plt.plot(times, totals)
    plt.plot(times, refusals)

    plt.legend()
    plt.show()

main()