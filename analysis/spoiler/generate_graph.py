import matplotlib.pyplot as plt
import json 
import matplotlib.cm as cm

def run(country):
    with open(f'./{country}.json') as file:
        data = json.load(file)

    data = data["metadata"]["method_counts"]

    del data["approval"]

    print(data)

    methods, counts = zip(*sorted(data.items(), key=lambda x: x[1], reverse=True))

    plt.figure(figsize=(10, 6))
    plt.barh(methods, counts, color="skyblue")
    plt.xlabel("Number of elections")
    plt.ylabel("Method")
    plt.title("Number of elections where a method is susceptible to spoiler effect")
    plt.gca().invert_yaxis()  
    plt.savefig(f'{country}.png')

run('america')
run('australia')
run('scotland')