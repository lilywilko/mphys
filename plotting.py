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

def main():
    values = []
    with open('5000_outbreaks_vs_vax_percentage.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader, None)
        for row in csv_reader:
            values.append((int(row[10]), int(row[11])))
        n=row[0]
    VariableVax(values,n)

main()