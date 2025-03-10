import json

methods = ['borda_lt_0.1', 'borda_lt_0.2', 'borda_lt_0.3', 'borda_lt_0.4', 'borda_lt_0.5', 'mention_lt_0.1', 'mention_lt_0.2', 'mention_lt_0.3', 'mention_lt_0.4', 'mention_lt_0.5']

def get_metadata_for_country(country):
    
    with open(f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/spoiler/spoiler_vs_fringe/results/{country}_spoiler_v_fringe.json') as file:
        data = json.load(file)

    method_counts = dict.fromkeys(methods, 0)
    total_counts = dict.fromkeys(methods, 0)

    for file in data:
        if file != 'files_with_no_scores':
            for candidate in data[file]:
                for method in methods:
                    if data[file][candidate][method]:
                        method_counts[method] += 1
                    total_counts[method] += 1

    print(method_counts)
    print(total_counts)

    all_data = {'total_counts': total_counts,
                'method_counts': method_counts}

    # write to output file
    output_file = f"/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/spoiler/spoiler_vs_fringe/results/{country}_svf_metadata.json"
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")

if __name__ == '__main__':
    get_metadata_for_country('america')
    get_metadata_for_country('australia')
    get_metadata_for_country('scotland')
    get_metadata_for_country('civs')