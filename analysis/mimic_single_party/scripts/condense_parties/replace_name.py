import os
import pandas as pd

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/keep_last_mentioned/raw_processed_data'

def get_party(candidate):
    if candidate == '[]':
        return candidate
    
    if candidate[3] == "(":
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
        return f"{party}"
    else:
        return candidate
    
def replace_names(filepath):
    df = pd.read_csv(filepath)

    candidates = set()
    for c in df.columns:
        if 'rank' in c: 
            candidates.update(list(df[c].unique()))

    if 'skipped' in candidates:
        candidates.remove('skipped')

    replace_dict = {}
    for c in candidates:
        replace_dict[c] = get_party(c)

    df.replace(replace_dict, inplace=True)
    out_path = filepath.replace('raw_processed_data','processed_data')

    if not os.path.exists('/'.join(out_path.split('/')[:-1])):
        os.makedirs('/'.join(out_path.split('/')[:-1]))
    print(out_path)
    df.to_csv(out_path, index=False)

def main():
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                full_path = os.path.join(dirpath, filename)
                replace_names(full_path)

if __name__ == '__main__':
    main()
