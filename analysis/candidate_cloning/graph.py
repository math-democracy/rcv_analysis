import matplotlib.pyplot as plt
import json

def graph(country):
    with open(f'./results/{country}_no_approval.json', 'r') as file:
        data = json.load(file)

    data = data["metadata"]["method_counts_by_percentage"]

    x_vals = sorted({float(x) for method in data.values() for x in method.keys()})

    methods = ["plurality","IRV","top-two","borda-pm","borda-om","borda-avg","top-3-truncation","condorcet","minimax","smith_plurality","smith_irv","smith-minimax","ranked-pairs","bucklin","approval","smith"]

    for method in methods:
        try:
            method_data = data[method]
            y_vals = [method_data.get(f"{x:.1f}", None) for x in x_vals]  # Fill missing with None
            plt.plot(x_vals, y_vals, marker='o', label=method)
        except:
            print('method not found')

    plt.xlabel("Probability of being placed above cloned candidate")
    plt.ylabel("Number of elections")
    plt.title(f"{country.capitalize()}: Spoiler effect from candidate cloning")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.subplots_adjust(left=0.1, right=0.7, top=0.8, bottom=0.2) 
    plt.savefig(f'{country}.png')
    plt.close()
    # plt.show()

graph('america')
# graph('australia')
# graph('scotland')