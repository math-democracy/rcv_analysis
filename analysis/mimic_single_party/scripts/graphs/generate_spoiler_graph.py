import matplotlib.pyplot as plt
import json 
import matplotlib.cm as cm
import numpy as np

def run(country):
    with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/borda_score/spoiler/winners_with_metadata.json') as file:
        borda_data = json.load(file)

    with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/spoiler/winners_with_metadata.json') as file:
        first_place_data = json.load(file)

    with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/mention_score/spoiler/winners_with_metadata.json') as file:
        mention_data = json.load(file)

    with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/borda/spoiler/winners_with_metadata.json') as file:
        borda_tb_data = json.load(file)

    with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/first_place/spoiler/winners_with_metadata.json') as file:
        first_place_tb_data = json.load(file)

    with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/mention/spoiler/winners_with_metadata.json') as file:
        mention_tb_data = json.load(file)

    with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/spoiler/scotland.json') as file:
        original_data = json.load(file)

    with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_last_mentioned/keep_first/spoiler/winners_with_metadata.json') as file:
        keep_first = json.load(file)

    with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_last_mentioned/keep_last/spoiler/winners_with_metadata.json') as file:
        keep_last = json.load(file)

    borda_data = borda_data["metadata"]["method_counts"]
    first_place_data = first_place_data["metadata"]["method_counts"]
    mention_data = mention_data["metadata"]["method_counts"]
    borda_tb_data = borda_tb_data["metadata"]["method_counts"]
    first_place_tb_data = first_place_tb_data["metadata"]["method_counts"]
    mention_tb_data = mention_tb_data["metadata"]["method_counts"]
    keep_first = keep_first["metadata"]["method_counts"]
    keep_last = keep_last["metadata"]["method_counts"]
    original_data = original_data["metadata"]["method_counts"]

    methods = ['plurality', 'borda-om', 'approval', 'top-3-truncation', 'top-two', 'bucklin', 'IRV', 'borda-avg', 'borda-pm', 'condorcet', 'smith', 'smith_plurality', 'minimax', 'ranked-pairs', 'smith_irv', 'smith-minimax']

    borda_data = {key: borda_data[key] for key in methods if key in borda_data}
    first_place_data = {key: first_place_data[key] for key in methods if key in first_place_data}
    mention_data = {key: mention_data[key] for key in methods if key in mention_data}
    borda_tb_data = {key: borda_tb_data[key] for key in methods if key in borda_tb_data}
    first_place_tb_data = {key: first_place_tb_data[key] for key in methods if key in first_place_tb_data}
    mention_tb_data = {key: mention_tb_data[key] for key in methods if key in mention_tb_data}
    keep_first = {key: keep_first[key] for key in methods if key in keep_first}
    keep_last = {key: keep_last[key] for key in methods if key in keep_last}
    original_data = {key: original_data[key] for key in methods if key in original_data}

    n = len(methods)
    r = np.arange(n) 
    width = 0.1

    borda_counts = list(borda_data.values())
    mention_counts = list(mention_data.values())
    first_place_counts = list(first_place_data.values())
    borda_tb_counts = list(borda_tb_data.values())
    mention_tb_counts = list(mention_tb_data.values())
    first_place_tb_counts = list(first_place_tb_data.values())
    keep_first_counts = list(keep_first.values())
    keep_last_counts = list(keep_last.values())
    original_counts = list(original_data.values())

    plt.figure(figsize=(20, 11))
    #plt.figure(figsize=(25, 11))
    print(original_counts)
    plt.bar(r, original_counts, color="black", width=width, label='original')
    plt.bar(r + 1*width, borda_counts, color="mediumblue", width=width, label='borda score')
    plt.bar(r + 2*width, mention_counts, color="cornflowerblue", width=width, label='mention score')
    plt.bar(r + 3*width, first_place_counts, color="lightsteelblue", width=width, label='first place score')
    plt.bar(r + 4*width, borda_tb_counts, color="maroon", width=width, label='borda tiebreaker')
    plt.bar(r + 5*width, mention_tb_counts, color="firebrick", width=width, label='mention tiebreaker')
    plt.bar(r + 6*width, first_place_tb_counts, color="lightcoral", width=width, label='first place tiebreaker')
    plt.bar(r + 7*width, keep_first_counts, color="blueviolet", width=width, label='keep first mentioned')
    plt.bar(r + 8*width, keep_last_counts, color="thistle", width=width, label='keep last mentioned')

    plt.xlabel("Count")
    plt.ylabel("Method")
    plt.xticks(r + width/2,methods,rotation=40) 
    plt.title("Num Elections with Spoiler Effect After Condensed by Various Methods")
    plt.legend() 
    plt.savefig(f'{country}.png')

# run('america')
# run('australia')
run('scotland')