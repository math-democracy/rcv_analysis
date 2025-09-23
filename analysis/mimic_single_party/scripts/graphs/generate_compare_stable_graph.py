import matplotlib.pyplot as plt
import json 
import matplotlib.cm as cm
import numpy as np

def run(country):
    with open('analysis/mimic_single_party/methods/tiebreaker/borda/scotland_results_top4.json') as file:
        borda_data = json.load(file)

    with open('analysis/mimic_single_party/methods/tiebreaker/first_place/scotland_results_top4.json') as file:
        first_place_data = json.load(file)

    with open('analysis/mimic_single_party/methods/tiebreaker/mention/scotland_results_top4.json') as file:
        mention_data = json.load(file)

    with open('analysis/stability/results/scotland_results_top4.json') as file:
        original_data = json.load(file)

    # with open('analysis/mimic_single_party/methods/first_last_mentioned/keep_first/scotland_results_top4.json') as file:
    #     keep_first = json.load(file)

    # with open('analysis/mimic_single_party/methods/first_last_mentioned/keep_last/scotland_results_top4.json') as file:
    #     keep_last = json.load(file)

    methods = ['plurality', 'borda-om', 'approval', 'top-3-truncation', 'top-two', 'bucklin', 'IRV', 'borda-avg', 'borda-pm', 'condorcet', 'smith', 'smith_plurality', 'minimax', 'ranked-pairs', 'smith_irv', 'smith-minimax']

    n = len(methods)
    r = np.arange(n) 
    width = 0.2
    
    borda_data = borda_data["metadata"]["method_counts"]
    first_place_data = first_place_data["metadata"]["method_counts"]
    mention_data = mention_data["metadata"]["method_counts"]
    # keep_first = keep_first["metadata"]["method_counts"]
    # keep_last = keep_last["metadata"]["method_counts"]
    original_data = original_data["metadata"]["method_counts"]

    borda_data = {key: borda_data[key] for key in methods if key in borda_data} #dict(sorted(borda_data.items()))
    first_place_data = {key: first_place_data[key] for key in methods if key in first_place_data} #dict(sorted(first_place_data.items()))
    mention_data = {key: mention_data[key] for key in methods if key in mention_data} #dict(sorted(mention_data.items()))
    # keep_first = {key: keep_first[key] for key in methods if key in keep_first} #dict(sorted(keep_first.items()))
    # keep_last = {key: keep_last[key] for key in methods if key in keep_last} #dict(sorted(keep_last.items()))
    original_data = {key: original_data[key] for key in methods if key in original_data} #dict(sorted(original_data.items()))

    borda_counts = list(borda_data.values())
    mention_counts = list(mention_data.values())
    first_place_counts = list(first_place_data.values())
    # keep_first_counts = list(keep_first.values())
    # keep_last_counts = list(keep_last.values())
    original_counts = list(original_data.values())

    print(borda_data)
    #borda_methods, borda_counts = zip(*sorted(borda_data.items(), key=lambda x: x[1], reverse=True))
    #mention_methods, mention_counts = zip(*sorted(mention_data.items(), key=lambda x: x[1], reverse=True))
    #first_place_methods, first_place_counts = zip(*sorted(first_place_data.items(), key=lambda x: x[1], reverse=True)

    #plt.figure(figsize=(15, 11))
    plt.figure(figsize=(20, 11))
    print(original_counts)

    # WITH OG
    plt.bar(r, original_counts, color="midnightblue", width=width, label='original')
    plt.bar(r + width, borda_counts, color="firebrick", width=width, label='borda score')
    plt.bar(r + 2*width, mention_counts, color="indianred", width=width, label='mention score')
    plt.bar(r+ 3*width, first_place_counts, color="lightcoral", width=width, label='first place score')
    # plt.bar(r+ 4*width, keep_first_counts, color="dodgerblue", width=width, label='keep first mentioned')
    # plt.bar(r+ 5*width, keep_last_counts, color="deepskyblue", width=width, label='keep last mentioned')

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