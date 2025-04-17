import pandas as pd
from collections import defaultdict
import re
import os
import multiprocessing
import csv 

root_dir = "/Users/belle/Desktop/build/rcv/raw_data/scotland"

def get_party(candidate):
    if candidate == "skipped":
        return None
    match = re.search(r"\((.*?)\)", candidate)

    if match:
        if match.group(1) == 'UNKNOWN' or match.group(1) == 'Ind' or match.group(1) == 'IND':
            return None
        else:
            return match.group(1)

def process_file(file_path):

    df = pd.read_csv(file_path)

    rank_cols = [col for col in df.columns if col.startswith("rank")]

    candidates = pd.unique(df[rank_cols].values.ravel())
    candidates = [c for c in candidates if c != "skipped"]

    party_to_candidates = defaultdict(list)
    for candidate in candidates:
        party = get_party(candidate)
        if party:
            party_to_candidates[party].append(candidate)

    print(candidates)
    return df, candidates, party_to_candidates

def count_two_in_row(df, party_to_candidates):
    votes = 0
    same_party = 0

    for _, row in df.iterrows():
        rank1 = row['rank1']
        rank2 = row['rank2']

        if rank1 == "skipped": #okay for rank2 to be skipped because it means they prefer no one to the next person
            continue

        party = get_party(rank1)
        if not party:
            print(rank1, rank2, "no party")
            continue

        same_party_candidates = party_to_candidates[party]
        if len(same_party_candidates) < 2:
            print(rank1, rank2, "no other cand of same party")
            continue

        votes += 1

        if rank2 in same_party_candidates and rank2 != rank1:
            same_party += 1
            print(rank1, rank2, "same")
        else:
            print(rank1, rank2, "diff")

    
    if votes == 0:
        return -1
    elif same_party == 0:
        return 0
    else:
        return same_party/votes

def count_second_somewhere(df, party_to_candidates):
    votes = 0
    same_party_elsewhere = 0

    rank_cols = [col for col in df.columns if col.startswith("rank")]

    rank_obj = {key: 0 for key in rank_cols}

    # print(rank_cols)

    for _, row in df.iterrows():
        rank1 = row['rank1']

        if rank1 == "skipped": #okay for rank2 to be skipped because it means they prefer no one to the next person
            continue

        party = get_party(rank1)
        if not party:
            # print(rank1, "no party")
            continue

        same_party_candidates = party_to_candidates[party]
        if len(same_party_candidates) < 2:
            # print(rank1, "no other cand of same party")
            continue

        votes += 1

        found_same_party_elsewhere = False
        for col in rank_cols[1:]:  # skip rank1
            candidate = row[col]
            if candidate != "skipped" and candidate in same_party_candidates and candidate != rank1:
                rank_obj[col] += 1
                found_same_party_elsewhere = True
                break

        if found_same_party_elsewhere:
            same_party_elsewhere += 1
        
    if votes == 0:
        return -1, None
    elif same_party_elsewhere == 0:
        return 0, None
    else:
        for key in rank_obj:
            rank_obj[key] = rank_obj[key] / votes
        return same_party_elsewhere/votes, rank_obj

def count_one_switch(df, party_to_candidates):
    votes = 0
    diff_party_next = 0

    rank_cols = [col for col in df.columns if col.startswith("rank")]

    rank_obj = {key: 0 for key in rank_cols}

    # print(rank_cols)

    for _, row in df.iterrows():
        rank1 = row['rank1']
        rank2 = row['rank2']

        if rank1 == "skipped": #okay for rank2 to be skipped because it means they prefer no one to the next person
            continue

        party = get_party(rank1)
        if not party:
            # print(rank1, "no party")
            continue

        same_party_candidates = party_to_candidates[party]
        if len(same_party_candidates) < 2:
            # print(rank1, "no other cand of same party")
            continue

        votes += 1

        if rank2 not in same_party_candidates:
            print(party_to_candidates)
            print(rank1, rank2)
            diff_party_next += 1
        
    if votes == 0:
        return -1
    elif diff_party_next == 0:
        return 0
    else:
        return diff_party_next/votes
    

def count_one_not(df, party_to_candidates):
    votes = 0
    skipped_next = 0

    rank_cols = [col for col in df.columns if col.startswith("rank")]

    rank_obj = {key: 0 for key in rank_cols}

    # print(rank_cols)

    for _, row in df.iterrows():
        rank1 = row['rank1']
        rank2 = row['rank2']

        if rank1 == "skipped": #okay for rank2 to be skipped because it means they prefer no one to the next person
            continue

        party = get_party(rank1)
        if not party:
            # print(rank1, "no party")
            continue

        same_party_candidates = party_to_candidates[party]
        if len(same_party_candidates) < 2:
            # print(rank1, "no other cand of same party")
            continue

        votes += 1

        if rank2 == "skipped":
            skipped_next += 1
        
    if votes == 0:
        return -1
    elif skipped_next == 0:
        return 0
    else:
        return skipped_next/votes
    
def count_all(df, party_to_candidates):
    votes = 0
    not_all = 0

    rank_cols = [col for col in df.columns if col.startswith("rank")]

    # rank_obj = {key: 0 for key in rank_cols}

    # print(rank_cols)

    for _, row in df.iterrows():
        rank1 = row['rank1']

        if rank1 == "skipped": #okay for rank2 to be skipped because it means they prefer no one to the next person
            continue

        party = get_party(rank1)
        if not party:
            # print(rank1, "no party")
            continue

        same_party_candidates = party_to_candidates[party]
        
        if len(same_party_candidates) < 2:
            # print(rank1, "no other cand of same party")
            continue

        cands_obj = {key: False for key in same_party_candidates}

        cands_obj[rank1] = True
        votes += 1
        

        for col in rank_cols[1:]:  # skip rank1
            candidate = row[col]
            if candidate != "skipped" and candidate in same_party_candidates and candidate != rank1:
                # rank_obj[col] += 1
                cands_obj[candidate] = True

        for c in cands_obj:
            if (cands_obj[c] == False):
                not_all += 1
                break
                

        
    if votes == 0:
        return -1
    elif not_all == 0:
        return 0
    else:
        return (votes - not_all)/votes

def process(file, results):
    df, candidates, party_to_candidates = process_file(file)
    # one_two = count_two_in_row(df, party_to_candidates)
    # one_something, rank_obj = count_second_somewhere(df, party_to_candidates)
    # c_all = count_all(df, party_to_candidates)
    one_change = count_one_not(df, party_to_candidates)

    d = {
        "file": file.replace("/Users/belle/Desktop/build/rcv/raw_data/scotland/processed_data/", ""),
        # "count_all": c_all
        # "one_two": one_two,
        # "one_something": one_something,
        "one_change": one_change,
        # "rank_obj": rank_obj
    }

    with open(results, mode='a', newline='') as file:
        writer = csv.writer(file)

        # write header if the file is empty
        if os.stat(results).st_size == 0:
            header = d.keys()
            writer.writerow(header)
            
        print(d)
        keys = d.keys()
        row = [d.get(key, '') for key in keys]
        writer.writerow(row)


def main():
    # loop through data files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                print(filename)
                full_path = os.path.join(dirpath, filename)
                lowest_folder = os.path.basename(os.path.dirname(full_path))

                results = f'./results6.csv'

                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process, args=(full_path, results))
                    p.start()
                    p.join(20)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(f'./error.txt', "a") as ef:
                            ef.write(f"{filename}, ")
                        p.terminate()
                        p.join()
                        print("\n")
            
if __name__ == '__main__':
    main()
