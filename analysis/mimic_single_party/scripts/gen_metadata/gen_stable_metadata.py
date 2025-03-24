import json

with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/metadata/stable_elections.json') as file:
    stable_metadata = json.load(file)

methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval']
score_methods = ['top4plurality','borda','mention','first_place']
completely_stable_elections = dict.fromkeys(score_methods,0)

method_counts = {m: {} for m in methods}#dict.fromkeys(methods,{})
for file in stable_metadata.keys():
    for sm in score_methods:
        completely_stable = True
        for m in stable_metadata[file]:
            if stable_metadata[file][m][sm] == False:
                completely_stable = False

        if completely_stable:
            completely_stable_elections[sm] += 1

    for m in stable_metadata[file]:
        results = ','.join(str(x) for x in list(stable_metadata[file][m].values())) 
        if results not in method_counts[m]:
            method_counts[m][results] = 1
        else:
            method_counts[m][results] += 1

        if m == 'plurality':
            print(method_counts['plurality'])

print(completely_stable_elections)

output_data = {'total_elections': len(stable_metadata.keys()),
                'completely_stable_elections': completely_stable_elections,
                'stable_metadata_KEY': {'bool,bool,bool,bool': 'top4plurality_isStable,borda_isStable,mention_isStable,first_place_isStable'},
                'stable_metadata': method_counts}
output_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/metadata/stable_elections_metadata.json'
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)
