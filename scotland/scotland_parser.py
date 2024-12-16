import pandas as pd
import numpy as np
import csv
import os

def parse_blt_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    metadata = lines[0].split()
    num_candidates, num_positions = int(metadata[0]), int(metadata[1])
    
    ballots = []
    i = 1
    while lines[i].strip() != "0":
        ballot_line = lines[i].strip()
        ballots.append(list(map(int, ballot_line.split())))
        i += 1
    
    candidates = []
    for line in lines[i+1:-1]:
        candidate = line.strip().strip('"')
        candidates.append(candidate.replace('"', ''))
    
    county = lines[-1]
    return {
        "num_positions": num_positions,
        "num_candidates": num_candidates,
        "ballots": ballots,
        "candidates": candidates,
        "county": county
    }


def parse_to_csv(data, outfilepath):
    candidates = [c for c in data['candidates']]
    ranks = ["rank" + str(i + 1) for i in range(len(candidates))]
    ballots = [b for b in data['ballots']]

    voter_id = 0

    all_votes = []

    for ballot in ballots:
        for voter in range(ballot[0]):
            c = {"voter_id": voter_id}
            c.update({rank: "skipped" for rank in ranks})
            for index, vote in enumerate(ballot[1:-1]):
                c[ranks[index]] = candidates[vote - 1]
            c['num_positions'] = data['num_positions']
            voter_id += 1
            all_votes.append(c)
    
    keys = all_votes[0].keys()

    with open(outfilepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(keys)
        for vote in all_votes:
            row = [vote.get(key, '') for key in keys]
            writer.writerow(row)


def validation_test(data):
    ballots = [b for b in data['ballots']]
    num_candidates = data['num_candidates']

    total_votes = 0
    votes_per_candidate = {i: [0 for i in range(num_candidates)] for i in range(1, num_candidates + 1)}

    for ballot in ballots:
        total_votes += ballot[0]
        for index, b in enumerate(ballot[1:-1]):
            votes_per_candidate[b][index] += ballot[0]

    return {"total_votes": total_votes, "candidate": votes_per_candidate}

def parser(infilepath, output_folder):
    data = parse_blt_file(infilepath)
    file_name = os.path.splitext(os.path.basename(infilepath))[0]
    outfilepath = f'{output_folder}/{file_name}.csv' 
    print("Converting blt to csv for " + file_name)
    print(validation_test(data))
    parse_to_csv(data, outfilepath)
    print("Data exported to " + outfilepath)