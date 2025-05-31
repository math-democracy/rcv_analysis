import os
import json

def get_metadata(file, distribution, model):
    states = file[distribution][model]
    list_of_sets = []

    for s in states:
        if states[s]:
            list_of_sets.append(set(states[s]))
    
    print(list_of_sets, distribution, model)
    if list_of_sets:
        int_result = list_of_sets[0]

        for s in list_of_sets:
            int_result = int_result.intersection(s)

        return list(int_result)
    else:
        return []


def main():
    full_path = '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/hpc_results/metadata_scripts/result_summary.json'
    with open(full_path) as file:
        data = json.load(file)
    metadata = {}

    distributions = ['distribution1','distribution2','distribution3']
    models = ["TTFF", "FTFF", "TFFF", "TTTF", "TTFT", "FFTF", "FFTT"]
    #states = ['California', 'Colorado', 'Indiana', 'Delaware', 'Michigan', 'New York', 'Pennsylvania', 'Alabama', 'North Carolina', 'Nebraska', 'Washington', 'Arizona', 'Florida', 'Alaska', 'Tennessee', 'Massachusetts', 'Wisconsin', 'North Dakota', 'Illinois', 'South Dakota', 'South Carolina', 'Kentucky']
    metadata = {d: {m: [] for m in models} for d in distributions}

    for d in distributions:
        for m in models:
            stable_methods = get_metadata(data, d, m)

            metadata[d][m] = stable_methods

    with open("/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/hpc_results/metadata_scripts/distribution_summary.json", "w") as f:
       json.dump(metadata, f, indent=4)

if __name__ == '__main__':
    main()