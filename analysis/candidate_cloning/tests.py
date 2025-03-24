import sys
import pandas as pd

sys.path.append('/Users/belle/Desktop/build/rcv_proposal')

import david_methods as dm
import main_methods as mm

from cloning import process_data

cloned = '/Users/belle/Desktop/build/rcv_proposal/analysis/candidate_cloning/files/alaskad11_Write-in.csv'
og = '/Users/belle/Desktop/build/rcv_proposal/raw_data/america/processed_data/Alaska/Alaska_11052024_StateHouseD11.csv'
profile = '/Users/belle/Desktop/build/rcv_proposal/raw_data/preference_profiles/american/Alaska/Alaska_11052024_StateHouseD11.csv'
# process_data(profile, 'alaskad11', './files', 'result3.csv', 0.5)

def process(full_path):
    df = pd.read_csv(full_path)

    columns = [c for c in df.columns if 'rank' in c]
    df = df[columns]
    df = df.value_counts().reset_index(name='Count')
    v =  mm.v_profile(full_path)
    candidates = list(v.candidates)
    candidates = [cand for cand in candidates if cand != 'skipped']
    num_cands = len(candidates)

    return dm.pairwise_comparisons_matrix(df, candidates, num_cands, None)


def clean_key(key):
    return key.split(" (")[0]  # Remove everything after ' ('

def compare_dicts(dict1, dict2):
    cleaned_dict1 = {clean_key(k): {clean_key(nk): v for nk, v in nv.items()} for k, nv in dict1.items()}
    cleaned_dict2 = {clean_key(k): {clean_key(nk): v for nk, v in nv.items()} for k, nv in dict2.items()}
    
    all_keys = set(cleaned_dict1.keys()).union(cleaned_dict2.keys())
    
    for key in all_keys:
        nested1 = cleaned_dict1.get(key, {})
        nested2 = cleaned_dict2.get(key, {})
        
        all_nested_keys = set(nested1.keys()).union(nested2.keys())
        
        for nested_key in all_nested_keys:
            val1 = nested1.get(nested_key)
            val2 = nested2.get(nested_key)
            if val1 != val2:
                print(f"Difference found for '{key}' -> '{nested_key}': {val1} vs {val2}")


c = process(cloned)
d = process(og)

print(c)
print(d)
compare_dicts(c, d)