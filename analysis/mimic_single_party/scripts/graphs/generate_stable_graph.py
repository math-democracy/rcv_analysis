import matplotlib.pyplot as plt
import json 
import matplotlib.cm as cm
import numpy as np

def run(country):
    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/borda_score/stability/scotland_results_top4.json') as file:
        borda_data = json.load(file)

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/stability/scotland_results_top4.json') as file:
        first_place_data = json.load(file)

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/mention_score/stability/scotland_results_top4.json') as file:
        mention_data = json.load(file)

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/scotland_results_top4.json') as file:
        original_data = json.load(file)

    methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval']
    n = len(methods)
    r = np.arange(n) 
    width = 0.2
    
    borda_data = borda_data["metadata"]["method_counts"]
    first_place_data = first_place_data["metadata"]["method_counts"]
    mention_data = mention_data["metadata"]["method_counts"]
    original_data = original_data["metadata"]["method_counts"]

    print(borda_data)
    #borda_methods, borda_counts = zip(*sorted(borda_data.items(), key=lambda x: x[1], reverse=True))
    #mention_methods, mention_counts = zip(*sorted(mention_data.items(), key=lambda x: x[1], reverse=True))
    #first_place_methods, first_place_counts = zip(*sorted(first_place_data.items(), key=lambda x: x[1], reverse=True))

    borda_counts = list(borda_data.values())
    mention_counts = list(mention_data.values())
    first_place_counts = list(first_place_data.values())
    original_counts = list(original_data.values())

    plt.figure(figsize=(15, 11))
    print(original_counts)

    # WITH OG
    plt.bar(r, original_counts, color="midnightblue", width=width, label='original')
    plt.bar(r + width, borda_counts, color="mediumblue", width=width, label='borda score')
    plt.bar(r + 2*width, mention_counts, color="cornflowerblue", width=width, label='mention score')
    plt.bar(r+ 3*width, first_place_counts, color="lightsteelblue", width=width, label='first place score')

    # #WITHOUT OG
    # plt.bar(r, borda_counts, color="mediumblue", width=width, label='borda score')
    # plt.bar(r + width, mention_counts, color="cornflowerblue", width=width, label='mention score')
    # plt.bar(r+ 2*width, first_place_counts, color="lightsteelblue", width=width, label='first place score')

    plt.xlabel("Count")
    plt.ylabel("Method")
    plt.xticks(r + width/2,methods,rotation=40) 
    plt.title("Num Unstable Elections After Condensed by Various Methods")
    plt.legend() 
    plt.savefig(f'{country}.png')

# run('america')
# run('australia')
run('scotland')