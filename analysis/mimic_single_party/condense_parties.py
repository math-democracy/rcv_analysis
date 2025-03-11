import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import csv
import json
import os
import pandas as pd
from itertools import groupby

with open('./analysis/mimic_single_party/party_breakdown.json') as file:
    party_breakdown = json.load(file)

df = pd.read_csv('./raw_data/scotland/processed_data/w-lothian12-ballots/LivingstonNorth_w-lothian12-03.csv')

def get_cands_to_keep(filepath, filename, method):
    if method == 'borda':
        with open(borda_file) as file:
            scores = json.load(file)
    elif method == 'mention':
        with open(mention_file) as file:
            scores = json.load(file)
    elif method == 'first_place':
        with open(first_place_file) as file:
            scores = json.load(file)

    party_info = party_breakdown[filepath]
    candidate_dict = party_info['party_dict']

    if filename in scores:
        candidate_scores = scores[filename]
        grouped_by_party = {i: [j[0] for j in j] for i, j in groupby(sorted(candidate_dict.items(), key = lambda x : x[1]), lambda x : x[1])}
        cands_to_keep = set()
        for party in grouped_by_party.values():
            keep = [i for i in candidate_dict.keys() if candidate_scores[i] == max(candidate_scores[title] for title in party)]
            cands_to_keep.update(keep)
    else:
        cands_to_keep = []
        with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/metadata/no_borda_score.txt', "a") as no_borda:
            no_borda.write(f"{method}: {filepath}\n")

    return cands_to_keep

borda_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/borda_scores/scotland_borda_scores.json'
mention_file =  '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/mention_scores/scotland_mention_scores.json'
first_place_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/scotland_first_place_ranks.json'

with open(mention_file) as file:
    scores = json.load(file)

filepath = 'raw_data/scotland/processed_data/w-lothian12-ballots/LivingstonNorth_w-lothian12-03.csv'
get_cands_to_keep(filepath, 'LivingstonNorth_w-lothian12-03.csv', scores)