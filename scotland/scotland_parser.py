import pandas as pd
import numpy as np
import csv
import os
import re
import random

def parse_file(filepath):
    with open(filepath, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]


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
    candidates = [normalize_parties(c) for c in data['candidates']]

    ranks = ["rank" + str(i + 1) for i in range(len(candidates))]
    ballots = [b for b in data['ballots']]

    voter_id = 0

    all_votes = []

    for ballot in ballots:
        for voter in range(ballot[0]):
            c = {"voterId": voter_id}
            c.update({rank: "skipped" for rank in ranks})
            for index, vote in enumerate(ballot[1:-1]):
                c[ranks[index]] = candidates[vote - 1]
            c['numSeats'] = data['num_positions']
            c['numCands'] = data['num_candidates']
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
        (r'Labour and Co-operative Party|Labour and Co‐operative Party', '(Labour and Co-operative Party)'),
        (r'Scottish Conservative and Unionist \(Con\)|Scottish Conservative and Unionist|Conservative and Unionist \(Con\)|\bCon\b|\bC\b|Conservatives|Conservative', '(Con)'),
        (r'Scottish National Party \(SNP\)|Scottish Nationals|Scottish National|\bSNP\b', '(SNP)'),
        (r'Scottish Greens - Delivering For Our Community|Scottish Greens - Think Global Act Local|Scottish Greens ‐ Think Global Act Local|Scottish Green Party \(Grn\)|Scottish Green Party|\bGrn\b|Scottish Greens|Scottish Green', '(Grn)'),
        (r'Scottish Unionist|Scottish Unionists| SU ', '(SU)'),
        (r'Scottish Labour Party|Aberdeen Labour \(Lab\)|Aberdeen Labour|\bLab\b|Labour', '(Lab)'),
        (r'Scottish Liberal Democrats \(LD\)|Scottish Liberal Democrats|\bLD\b|Liberal Democrat Focus Team|Liberal Democrats|Liberal Democrat', '(LD)'),
        (r'Independent Green Voice - Organic Green Scotland|Independent Green Voice', '(IGV)'),
        (r'Independents|Independent|\bInd\b', '(Ind)'),
        (r'Scottish Libertarian Party|\bLibtn\b|Libertarians|Libertarian', '(Libtn)'),
        (r'\bSC\b|Scottish Christian|\bChr\b', '(SC)'),
        (r'\bSol\b|Solidarity', '(Sol)'),
        (r'UK Independence Party|UK Independence|UKIP', '(UKIP)'),
        (r'Scottish Trade Unionist and Socialist Coalition \(Soc\)|Scottish Trade Unionist and Socialist Coalition|\bSoc\b|Scottish Trade Unionist and Socialist|Scottish Socialist|\bSSP\b', '(Soc)'),
        (r'Scottish Family Party Pro-Family, Pro-Marriage, Pro-Life \(SFP\)|Scottish Family Party Pro-Family, Pro-Marriage, Pro-Life|Scottish Family Party: Pro‐Family, Pro‐Marriage|Scottish Family Party - Putting Families First|Scottish Family|\bSFP\b', '(SFP)'),
        (r'Trade Unionist|TUSC', '(TUSC)'),
        (r'\bNF\b|National Front', '(NF)'),
        (r'Alba Party: Yes to Scottish Independence|Alba Party for Independence|Alba Party for independence \(API\)|Alba Party for independence|Alba Party for Independence|Alba Party|API|ALBA|Alba', '(Alba)'),
        (r'\bSDP\b|Social Democratic', '(SDP)'),
        (r'\bGF\b|Glasgow First', '(Glasgow First)'),
        (r'Britannica', '(Britannica)'),
        (r'\bPir\b|Pirate', '(Pir)'),
        (r'\bComm\b|Communist', '(Comm)'),
        (r'British National Party|\bBNP\b', '(BNP)'),
        (r'Christian People|\bCPA\b', '(CPA)'),
        (r'\bSSC\b|Scottish Senior', '(SSC)'),
        (r'\bMVR\b|Monster Raving', '(MVR)'),
        (r'Sovereignty', '(Sovereignty)'),
        (r'Volt UK', '(Volt UK)'),
        (r'Freedom Alliance. Leave Our Children Alone.|Freedom Alliance', '(Freedom Alliance)'),
        (r'\bVanguard\b', '(Vanguard)'),
        (r'\bSEFP\b', '(SEFP)'),
        (r'\bLib\b|Liberal Party', '(Liberal)'),
        (r'East Dunbartonshire|EDIA', '(EDIA)'),
        (r'Borders', '(Scottish Borders)'),
        (r'East Kilbride|EKA', '(EKA)'),
        (r'\bCICA\b', '(CICA)'),
        (r'\bRubbish\b', '(Rubbish)'),
        (r'\bBritish Unionist\b', '(British Unionist)'),
        (r'\bOMG\b', '(OMG)'),
        (r'West Dunbartonshire Community Party|West Dunbartonshire|\bWDuns\b|\bWDCP\b', '(WDuns)')
    ]
    
    # print("old", party)
    for pattern, replacement in replacements:
        if re.search(pattern, party):
            party = re.sub(pattern, replacement, party)
            break
    
    party = party.replace('((', '(').replace('))', ')').replace('  ', '').replace(',', '')
    # print("new", party)
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
    # random_int = random.randint(1, 15)
    # if random_int == 2:
    print(infilepath)
    data = parse_file(infilepath)
    county = data["county"].replace(" ", "").replace("/", "").replace('"', '')
    file_name = os.path.splitext(os.path.basename(infilepath))[0]
    outfilepath = f'{output_folder}/{county}_{file_name}.csv' 
    print("Converting blt to csv for " + file_name)
    print(validation_test(data))
    parse_to_csv(data, outfilepath)
    print("Data exported to " + outfilepath)    


# test_file = '/Users/belle/Downloads/Scotland data, LEAP parties/e-ayrshire22/Ward2.csv'

# parser(test_file, './data')