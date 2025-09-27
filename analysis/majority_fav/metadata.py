import json

with open('output.json', 'r') as f:
    data = json.load(f)

methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']
results_summary = {}

for country, files in data.items():
    none_count = 0
    not_none_count = 0
    method_false_counts = {method: 0 for method in methods}

    for file, content in files.items():
        if content is None:
            none_count += 1
        else:
            not_none_count += 1
            for method in methods:
                if not content.get(method):  
                    method_false_counts[method] += 1

    results_summary[country] = {
        "none_count": none_count, # no majority winner
        "not_none_count": not_none_count, # yes majority winner
        "method_false_count": method_false_counts
    }


print(results_summary)