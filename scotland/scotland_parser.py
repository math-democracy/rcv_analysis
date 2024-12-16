import pandas as pd
import numpy as np
import csv
import os
import re

def parse_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    lines = [re.sub(r',\s*$', '', line) for line in lines] #to deal with , at the end of csv files
    
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
    for c in candidates:
        c = normalize_parties(c)
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

def normalize_parties(party):
    replacements = [
        (r'\(Con\)|\(C\)|Conservative', 'Con'),
        (r'\(SNP\)|Scottish National', 'SNP'),
        (r'\(Grn\)|Scottish Green', 'Grn'),
        (r'Scottish Unionist|\(SU\)', 'SU'),
        (r'\(Lab\)|Labour', 'Lab'),
        (r'\(LD\)|Liberal Democrat', 'LD'),
        (r'\(Ind\)|Independent', 'Ind'),
        (r'\(Libtn\)|Libertarian', 'Libtn'),
        (r'\(SC\)|Scottish Christian|\(Chr\)', 'SC'),
        (r'\(Sol\)|Solidarity', 'Sol'),
        (r'UK Independence|UKIP', 'UKIP'),
        (r'SFP|Scottish Family', 'SFP'),
        (r'Trade Unionist|TUSC', 'TUSC'),
        (r'\(NF\)|National Front', 'NF'),
        (r'\(Soc\)|Scottish Trade Unionist and Socialist|Scottish Socialist|SSP', 'Soc'),
        (r'API|ALBA|Alba', 'Alba'),
        (r'\(SDP\)|Social Democratic', 'SDP'),
        (r'\(GF\)|Glasgow First', 'Glasgow First'),
        (r'Britannica', 'Britannica'),
        (r'\(Pir\)|Pirate', 'Pir'),
        (r'\(Comm\)|Communist', 'Comm'),
        (r'British National Party|BNP', 'BNP'),
        (r'Christian People|CPA', 'CPA'),
        (r'\(SSC\)|Scottish Senior', 'SSC'),
        (r'\(MVR\)|Monster Raving', 'MVR'),
        (r'Sovereignty', 'Sovereignty'),
        (r'Volt UK', 'Volt UK'),
        (r'Freedom Alliance', 'Freedom Alliance'),
        (r'Vanguard', 'Vanguard'),
        (r'\(SEFP\)', 'SEFP'),
        (r'\(Lib\)|Liberal Party', 'Liberal'),
        (r'East Dunbartonshire|EDIA', 'EDIA'),
        (r'Borders', 'Scottish Borders'),
        (r'East Kilbride|EKA', 'EKA'),
        (r'CICA', 'CICA'),
        (r'Rubbish', 'Rubbish'),
        (r'British Unionist', 'British Unionist'),
        (r'OMG', 'OMG'),
        (r'West Dunbartonshire|\(WDuns\)|WDCP', 'WDuns')
    ]

    for pattern, replacement in replacements:
        party = re.sub(pattern, replacement, party)
        
    return party

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
    print(infilepath)
    data = parse_file(infilepath)
    file_name = os.path.splitext(os.path.basename(infilepath))[0]
    outfilepath = f'{output_folder}/{file_name}.csv' 
    print("Converting blt to csv for " + file_name)
    print(validation_test(data))
    parse_to_csv(data, outfilepath)
    print("Data exported to " + outfilepath)    
