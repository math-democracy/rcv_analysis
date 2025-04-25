import json

with open('output.json', 'r') as f:
    data = json.load(f)

methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']
results_summary = {}

for country, files in data.items():
    none_count = 0
    not_none_count = 0
    method_false_counts = {method: 0 for method in methods}
    # all_false_count = 0

    for file, content in files.items():
        if content is None:
            none_count += 1
        else:
            not_none_count += 1
            # all_false = True
            for method in methods:
                if not content.get(method):  
                    method_false_counts[method] += 1
                # else:
                #     all_false = False
            # if all_false:
            #     all_false_count += 1


    results_summary[country] = {
        "none_count": none_count,
        "not_none_count": not_none_count,
        "method_false_count": method_false_counts
        # "all_false_count": all_false_count
    }


print(results_summary)