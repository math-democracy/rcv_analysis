import matplotlib.pyplot as plt
import json 
import matplotlib.cm as cm

def run(country):
    with open(f'./{country}.json') as file:
        data = json.load(file)

    data = data["metadata"]["method_counts"]

    methods, counts = zip(*sorted(data.items(), key=lambda x: x[1], reverse=True))

    plt.figure(figsize=(10, 6))
    plt.barh(methods, counts, color="skyblue")
    plt.xlabel("Count")
    plt.ylabel("Method")
    plt.title("Method Counts Bar Chart")
    plt.gca().invert_yaxis()  
    plt.savefig(f'{country}.png')

run('america')
run('australia')
run('scotland')