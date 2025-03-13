import json

def is_fringe(scores, candidate, dict, prefix, filename, no_score):
    # get is fringe for 10-50%
    
    for i in range(1,10):
        threshold = i/10

        # get score of candidate with highest score
        top_score = max(scores.values())

        if candidate in scores:
            candidate_score = scores[candidate]
        else:
            candidate_score = -1
            
        
        if candidate_score <= (top_score * threshold):
            dict[f'{prefix}_{str(threshold)}'] = True
        else:
            dict[f'{prefix}_{str(threshold)}'] = False

    return dict

def process_json(data):
    processed = {}
    for country, files in data.items():
        processed[country] = {}
        for path, candidates in files.items():
            new_key = path.split("/")[-1]  # Extract last part of path
            processed[new_key] = candidates
    return processed

def get_data_for_country(country):
    no_score = set()

    with open(f'../{country}.json', 'r') as file:
        spoiler_file = json.load(file)

    with open(f'../../fringe/borda_scores/{country}_borda_scores.json', 'r') as file:
        borda_scores = json.load(file)

    with open(f'../../fringe/mention_scores/{country}_mention_scores.json', 'r') as file:
        mention_scores = json.load(file)
    
    with open('/Users/belle/Desktop/build/rcv_proposal/analysis/first_place_analysis/first_place_ranks.json') as file:
        plurality_scores = json.load(file)
        plurality_scores = process_json(plurality_scores)
        print(plurality_scores)

    files = spoiler_file['winners'].keys()
    spoiler_metadata = spoiler_file['winners']

    # fringe_methods = ['borda_lt_10', 'borda_lt_20', 'borda_lt_30','borda_lt_40','borda_lt_50',
    #                     'mention_lt_10', 'mention_lt_20', 'mention_lt_30','mention_lt_40','mention_lt_50']

    all_data = dict.fromkeys(files)

    for file in files:
        print(file)
        spoiler_changes = spoiler_metadata[file]
        spoiler_cands = []
        spoiler_methods = {}

        if file.split('/')[-1] in borda_scores:
            borda = borda_scores[file.split('/')[-1]]
            borda = dict(sorted(borda.items(), key=lambda item: item[1], reverse=True))

            mention = mention_scores[file.split('/')[-1]]
            mention = dict(sorted(mention.items(), key=lambda item: item[1], reverse=True))

            plurality = plurality_scores[file.split('/')[-1]]
            plurality = dict(sorted(plurality.items(), key=lambda item: item[1], reverse=True))

        else:
            no_score.add(file)
    

        # get all spoiler candidates for file
        for changes in spoiler_changes:
            spoiler_cands.append(changes['candidate_removed'])
            m = []
            for method in changes['changes']:
                m.append(method)
            spoiler_methods[changes['candidate_removed']] = m
        
        print(spoiler_methods)
        spoilers_dict = dict.fromkeys(spoiler_cands,0)

        for cand in spoiler_cands:
            methods_dict = {}
            if country == 'civs':
                print(cand)
                cand = int(float(cand))
            methods_dict = is_fringe(borda, cand, methods_dict, 'borda_lt', file, no_score)
            methods_dict = is_fringe(mention, cand, methods_dict, 'mention_lt', file, no_score)
            methods_dict = is_fringe(plurality, cand, methods_dict, 'plurality_lt', file, no_score)
            methods_dict['methods'] = spoiler_methods[cand]
            spoilers_dict[cand] = methods_dict
            
        
        all_data[file] = spoilers_dict

    all_data['files_with_no_scores'] = list(no_score)

    # write to output file
    output_file = f"./new_results/{country}_spoiler_v_fringe.json"
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")

if __name__ == '__main__':
    get_data_for_country('australia')
    get_data_for_country('america')
    get_data_for_country('scotland')
    # get_data_for_country('civs')

    