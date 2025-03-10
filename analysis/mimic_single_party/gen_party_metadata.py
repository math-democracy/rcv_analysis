import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import os
import pandas as pd
import json
from collections import Counter

files = {}
def process_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                print(f'processing: {filename}')
                full_path = os.path.join(dirpath, filename)
                prof = mm.v_profile(full_path)
                candidates = [c for c in prof.candidates if c != 'skipped']

                parties = []
                party_dict = {}
                for candidate in candidates:
                    if candidate[0] == "(":
                        party = candidate[1:candidate.find(")")]
                    else:
                        left = candidate.rfind("(")
                        right = candidate[left:].rfind(")")
                        if right == -1:
                            right = -1
                        else:
                            right = left + right
                        party = candidate[left+1:right]

                    if party != 'Ind' and party != 'UNKNOWN':
                        party_dict[candidate] = party
                    else:
                        party_dict[candidate] = candidate

                    parties.append(party)

                #print(candidates, parties)
                info = {'candidates': candidates,
                        'party_dict': party_dict,
                        'parties': Counter(parties)}
            
                files[full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')] = info

    return files


root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data'
process_files(root_dir)

output_file = "/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/party_breakdown.json"
with open(output_file, "w") as f:
    json.dump(files, f, indent=4)

