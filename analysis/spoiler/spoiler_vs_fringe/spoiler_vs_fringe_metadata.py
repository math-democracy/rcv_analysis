import json

methods = ['borda_lt_0.1', 'borda_lt_0.2', 'borda_lt_0.3', 'borda_lt_0.4', 'borda_lt_0.5', 'borda_lt_0.6', 'borda_lt_0.7', 'borda_lt_0.9', 'mention_lt_0.1', 'mention_lt_0.2', 'mention_lt_0.3', 'mention_lt_0.4', 'mention_lt_0.5', 'mention_lt_0.6', 'mention_lt_0.7', 'mention_lt_0.8', 'mention_lt_0.9', 'plurality_lt_0.1', 'plurality_lt_0.2', 'plurality_lt_0.3', 'plurality_lt_0.4', 'plurality_lt_0.5', 'plurality_lt_0.6', 'plurality_lt_0.7', 'plurality_lt_0.8', 'plurality_lt_0.9']

def get_metadata_for_country(country):
    
    with open(f'./new_results/{country}_spoiler_v_fringe.json') as file:
        data = json.load(file)

    fringe_count = {method: {} for method in methods}    
    total_counts = {method: set() for method in methods}
    # fringe_count = dict.fromkeys(methods, 0)
    #total_counts = dict.fromkeys(methods, set())
    # total_counts = dict.fromkeys(methods, 0)
    for file in data:
        if file != 'files_with_no_scores':
            for candidate in data[file]:
                for method in methods:
                    if data[file][candidate][method]:
                        all_m = data[file][candidate]["methods"]
                        
                        for m in all_m:
                            if m not in fringe_count[method]:
                                fringe_count[method][m] = set()

                            fringe_count[method][m].add(file)

                           
                    total_counts[method].add(file)

    # print(len(write))
    # print(fringe_count)
    # print(fringe_count.items())
    # # print(total_counts)

    all_data = {'total_counts': {total: len(e) for total, e in total_counts.items()},
                "fringe_count": {
        method: {m: len(files) for m, files in fringe_count[method].items()}
        for method in fringe_count
    }}

    # all_data = {'total_counts': total_counts, 'fringe_count': fringe_count}
    # write to output file
    output_file = f"./new_results/{country}_svf_metadata.json"
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")

if __name__ == '__main__':
    get_metadata_for_country('australia')
    get_metadata_for_country('america')
    get_metadata_for_country('scotland')
    # get_metadata_for_country('civs')