import matplotlib.pyplot as plt
import json 
import matplotlib.cm as cm
import numpy as np

def run(country):
    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/borda/scotland_results_top4.json') as file:
        new_borda_data = json.load(file)

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/first_place/scotland_results_top4.json') as file:
        new_first_place_data = json.load(file)

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/mention/scotland_results_top4.json') as file:
        new_mention_data = json.load(file)

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/borda_score/stability/scotland_results_top4.json') as file:
        borda_data = json.load(file)

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/stability/scotland_results_top4.json') as file:
        first_place_data = json.load(file)

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/mention_score/stability/scotland_results_top4.json') as file:
        mention_data = json.load(file)

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_last_mentioned/keep_first/scotland_results_top4.json') as file:
        keep_first_data = json.load(file)

    # with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_last_mentioned/keep_last/scotland_results_top4.json') as file:
    #     keep_last = json.load(file)

    methods = ['plurality', 'borda-om', 'approval', 'top-3-truncation', 'top-two', 'bucklin', 'IRV', 'borda-avg', 'borda-pm', 'condorcet', 'smith', 'smith_plurality', 'minimax', 'ranked-pairs', 'smith_irv', 'smith-minimax']

    n = len(methods)
    r = np.arange(n) 
    width = 0.13
    
    borda_data = borda_data["metadata"]["method_counts"]
    first_place_data = first_place_data["metadata"]["method_counts"]
    mention_data = mention_data["metadata"]["method_counts"]
    new_borda_data = new_borda_data["metadata"]["method_counts"]
    new_first_place_data = new_first_place_data["metadata"]["method_counts"]
    new_mention_data = new_mention_data["metadata"]["method_counts"]
    keep_first_data = keep_first_data["metadata"]["method_counts"]

    borda_data = {key: borda_data[key] for key in methods if key in borda_data} #dict(sorted(borda_data.items()))
    first_place_data = {key: first_place_data[key] for key in methods if key in first_place_data} #dict(sorted(first_place_data.items()))
    mention_data = {key: mention_data[key] for key in methods if key in mention_data} #dict(sorted(mention_data.items()))
    new_borda_data = {key: new_borda_data[key] for key in methods if key in new_borda_data} #dict(sorted(borda_data.items()))
    new_first_place_data = {key: new_first_place_data[key] for key in methods if key in new_first_place_data} #dict(sorted(first_place_data.items()))
    new_mention_data = {key: new_mention_data[key] for key in methods if key in new_mention_data}
    keep_first_data = {key: keep_first_data[key] for key in methods if key in keep_first_data}

    borda_counts = list(borda_data.values())
    mention_counts = list(mention_data.values())
    first_place_counts = list(first_place_data.values())
    new_borda_counts = list(new_borda_data.values())
    new_mention_counts = list(new_mention_data.values())
    new_first_place_counts = list(new_first_place_data.values())
    keep_first_counts = list(keep_first_data.values())

    print(borda_data)
    #borda_methods, borda_counts = zip(*sorted(borda_data.items(), key=lambda x: x[1], reverse=True))
    #mention_methods, mention_counts = zip(*sorted(mention_data.items(), key=lambda x: x[1], reverse=True))
    #first_place_methods, first_place_counts = zip(*sorted(first_place_data.items(), key=lambda x: x[1], reverse=True)

    #plt.figure(figsize=(15, 11))
    plt.figure(figsize=(20, 11))

    # WITH OG
    plt.bar(r + 0*width, borda_counts, color="midnightblue", width=width, label='old borda score')
    plt.bar(r + 1*width, new_borda_counts, color="lightsteelblue", width=width, label='new borda score')
    plt.bar(r + 2*width, mention_counts, color="maroon", width=width, label='old mention score')
    plt.bar(r + 3*width, new_mention_counts, color="lightcoral", width=width, label='new mention score')
    plt.bar(r + 4*width, first_place_counts, color="darkgreen", width=width, label='old first place score')
    plt.bar(r + 5*width, new_first_place_counts, color="lightgreen", width=width, label='new first place score')
    plt.bar(r + 6*width, keep_first_counts, color="hotpink", width=width, label='keep first mentioned')
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