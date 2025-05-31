import os
import json

def get_metadata(full_path):
    with open(full_path) as file:
        data = json.load(file)

    unstable_elections = data['metadata']['method_counts']

    stable_methods = []
    for method in unstable_elections:
        if unstable_elections[method] == 0:
            stable_methods.append(method)

    return stable_methods


def main():

    metadata = {}

    distributions = ['distribution1','distribution2','distribution3']
    models = ["TTFF", "FTFF", "TFFF", "TTTF", "TTFT", "FFTF", "FFTT"]
    states = ['California', 'Colorado', 'Indiana', 'Delaware', 'Michigan', 'New York', 'Pennsylvania', 'Alabama', 'North Carolina', 'Nebraska', 'Washington', 'Arizona', 'Florida', 'Alaska', 'Tennessee', 'Massachusetts', 'Wisconsin', 'North Dakota', 'Illinois', 'South Dakota', 'South Carolina', 'Kentucky']
    
    metadata = {d: {m: {s: None for s in states} for m in models} for d in distributions}

    states = set()
    root_dir = '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/hpc_results/metadata'
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            #print(filename)
            if filename.endswith('.json'):
                full_path = os.path.join(dirpath, filename)
                state = filename.split('_')[0]
                distribution = filename.split('_')[1]
                model = filename[-9:-5]

                stable_methods = get_metadata(full_path)

                metadata[distribution][model][state] = stable_methods

    with open("/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/hpc_results/metadata_scripts/result_summary.json", "w") as f:
       json.dump(metadata, f, indent=4)

if __name__ == '__main__':
    main()