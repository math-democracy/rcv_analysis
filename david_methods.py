def update_rankings(row, cands_to_keep):
    filtered_ranking = [candidate for candidate in row if candidate in cands_to_keep]
    updated_ranking = filtered_ranking + ['skipped'] * (len(row) - len(filtered_ranking))
    return updated_ranking


def pairwise_comparisons_matrix(pref_profile, cands_to_keep, num_cands, shortcut):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile= new_profile

    # Shortcut: Restrict to top 5 candidates by plurality scores
    if shortcut and len(cands_to_keep) > 5:
        plurality_scores = {cand: 0 for cand in cands_to_keep}
        for k in range(len(pref_profile)):
            plurality_scores[pref_profile.at[k, 'rank1']] += pref_profile.at[k, 'Count']

        # Get the top 5 candidates by plurality score
        top_candidates = sorted(plurality_scores, key=plurality_scores.get, reverse=True)[:5]
    else:
        top_candidates = cands_to_keep

    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]

    # Initialize a pairwise comparison matrix
    pairwise_matrix = {cand: {opponent: 0 for opponent in top_candidates if opponent != cand} for cand in top_candidates}

    # Perform pairwise comparisons
    for _, row in pref_profile.iterrows():
        count = row['Count']
        for cand in top_candidates:
            for opponent in top_candidates:
                if cand != opponent:
                    # Find the rank of each candidate
                    rank_cand = next((rank for rank, c in enumerate(row[rank_columns], start=1) if c == cand), float('inf'))
                    rank_opponent = next((rank for rank, c in enumerate(row[rank_columns], start=1) if c == opponent), float('inf'))

                    # Increment pairwise count if one candidate is ranked higher
                    if rank_cand < rank_opponent:
                        pairwise_matrix[cand][opponent] += count
    return pairwise_matrix

#Borda pessimistic model
def Borda_PM(pref_profile, cands_to_keep, num_cands):
    
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile
    
    max_score = len(cands_to_keep) - 1
    
    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    cands = pd.unique(pref_profile[rank_columns].values.ravel()).tolist()
    cands = [cand for cand in cands if cand != 'skipped']
    
    cand_scores = {cand: 0 for cand in cands}
    for k in range(len(pref_profile)):
        count = pref_profile.at[k, 'Count']
        for i in range(1, len(rank_columns) + 1):
            rank_col = 'rank' + str(i)
            candidate = pref_profile.at[k, rank_col]
            if candidate == 'skipped':
                break
            if candidate in cands:
                cand_scores[candidate] += (max_score - (i - 1)) * count
    #print(cand_scores)
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return winners

#Borda optimistic
def Borda_OM(pref_profile, cands_to_keep, num_cands, keep_UWI):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    # Get non-UWI candidates
    if keep_UWI:
        non_UWI_cands = cands_to_keep
        max_score = len(cands_to_keep) - 1
    else:
        non_UWI_cands = [cand for cand in cands_to_keep if 'write' not in cand and 'Write' not in cand and cand != 'UWI']
        max_score = len(non_UWI_cands) - 1

    # Handle special cases with few candidates
    if len(non_UWI_cands) == 1:
        return non_UWI_cands  # Return the only non-write-in candidate
    elif len(non_UWI_cands) == 2:
        # Only two non-write-in candidates: count first-place votes
        first_place_counts = {cand: 0 for cand in non_UWI_cands}
        rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
        for k in range(len(pref_profile)):
            count = pref_profile.at[k, 'Count']
            first_rank = pref_profile.at[k, 'rank1']
            if first_rank in first_place_counts:
                first_place_counts[first_rank] += count
        max_first_place = max(first_place_counts.values())
        return [cand for cand, count in first_place_counts.items() if count == max_first_place]

    # Normal case: more than two non-write-in candidates
    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    cands = pd.unique(pref_profile[rank_columns].values.ravel()).tolist()
    cands = [cand for cand in cands if cand != 'skipped']

    # Initialize scores
    cand_scores = {cand: 0 for cand in cands}

    # Loop through preference profile and calculate scores
    for k in range(len(pref_profile)):
        count = pref_profile.at[k, 'Count']
        cutoff_rank = next(
            (i for i, col in enumerate(rank_columns, start=1) if pref_profile.at[k, f'rank{i}'] == 'skipped'),
            len(rank_columns)
        )
        for i in range(1, len(rank_columns) + 1):
            rank_col = f'rank{i}'
            candidate = pref_profile.at[k, rank_col]
            if candidate == 'skipped':
                break
            if candidate in cands:
                cand_scores[candidate] += max(0, (max_score - (i - 1))) * count  # Prevent negative scores

        unranked_candidates = [
            cand for cand in cands 
            if cand not in pref_profile.loc[k, rank_columns].values 
            and 'write' not in cand.lower() 
            and cand != 'UWI'
        ]
        for unranked_cand in unranked_candidates:
            cand_scores[unranked_cand] += max(0, (max_score - cutoff_rank+1)) * count
    #print(cand_scores)
    # Find the winner(s)
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return winners


#Borda average
def Borda_AVG(pref_profile, cands_to_keep, num_cands, keep_UWI):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    if keep_UWI:
        max_score = len(cands_to_keep) - 1
    else:
        non_UWI_cands = [cand for cand in cands_to_keep if 'write' not in cand and 'Write' not in cand and cand != 'UWI']
        max_score = len(non_UWI_cands) - 1

    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    cands = pd.unique(pref_profile[rank_columns].values.ravel()).tolist()
    cands = [cand for cand in cands if cand != 'skipped']

    cand_scores = {cand: 0 for cand in cands}

    for k in range(len(pref_profile)):
        count = pref_profile.at[k, 'Count']
        # Find the cutoff rank for this ballot (i.e., the first 'skipped' or end of ranks)
        cutoff_rank = next(
            (i for i, col in enumerate(rank_columns, start=1) if pref_profile.at[k, f'rank{i}'] == 'skipped'),
            len(rank_columns)
        )
        # Loop through rank columns and allocate scores
        for i in range(1, len(rank_columns) + 1):
            rank_col = f'rank{i}'
            candidate = pref_profile.at[k, rank_col]

            if candidate == 'skipped':
                break

            if candidate in cands:
                cand_scores[candidate] += (max_score - (i - 1)) * count

        # Handle unranked candidates by distributing remaining points
        unranked_candidates = [
            cand for cand in cands
            if cand not in pref_profile.loc[k, rank_columns].values
            and (keep_UWI or ('write' not in cand.lower() and cand != 'UWI'))
        ]

        # If there are unranked candidates, distribute the remaining points
        if unranked_candidates:
            remaining_points = sum(max_score - i for i in range(len(rank_columns), len(cands_to_keep)))
            points_per_candidate = remaining_points / len(unranked_candidates)

            for unranked_cand in unranked_candidates:
                cand_scores[unranked_cand] += points_per_candidate * count

    # Determine the winner(s)
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return winners

#Borda points scheme
def Borda_trunc_points_scheme(pref_profile, cands_to_keep, num_cands, points_scheme):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    # Determine how many ranks we have and extend the points scheme with 0's if needed
    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    num_ranks = len(rank_columns)
    truncated_points_scheme = points_scheme + [0] * (num_ranks - len(points_scheme))  # Append 0s if needed

    cands = pd.unique(pref_profile[rank_columns].values.ravel()).tolist()
    cands = [cand for cand in cands if cand != 'skipped']

    cand_scores = {cand: 0 for cand in cands}

    for k in range(len(pref_profile)):
        count = pref_profile.at[k, 'Count']
        
        # Loop through rank columns and allocate points based on the truncated points scheme
        for i in range(1, num_ranks + 1):
            rank_col = f'rank{i}'
            candidate = pref_profile.at[k, rank_col]

            if candidate == 'skipped':
                break

            if candidate in cands:
                cand_scores[candidate] += truncated_points_scheme[i - 1] * count

    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return winners

def Bucklin(pref_profile, cands_to_keep, num_cands):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    # Initialize scores for candidates to 0
    scores = {cand: 0.0 for cand in cands_to_keep}
    threshold = pref_profile['Count'].sum() / 2  # Majority threshold
    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]

    for round_idx in range(1, len(rank_columns) + 1):
        # Update scores for the current round
        for k in range(len(pref_profile)):
            count = pref_profile.at[k, 'Count']
            for i in range(1, round_idx + 1):
                rank_col = f'rank{i}'
                candidate = pref_profile.at[k, rank_col]
                if candidate in cands_to_keep:
                    scores[candidate] += count

        # Check if any candidate has surpassed the majority threshold
        surpassing_candidates = {cand: score for cand, score in scores.items() if score > threshold}
        if surpassing_candidates:
            max_score = max(surpassing_candidates.values())
            winners = [cand for cand, score in surpassing_candidates.items() if score == max_score]
            return winners  # Return the candidate(s) with the most votes above the threshold

    # At the end of all rounds, if no majority is reached
    max_score = max(scores.values())
    winners = [cand for cand, score in scores.items() if score == max_score]
    return winners

import random

def plurality(pref_profile, cands_to_keep, num_cands):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    cands = cands_to_keep[:]
    votes = {cand: 0 for cand in cands}

    # Count first-choice votes
    
    for i in range(len(pref_profile)):
        count = pref_profile.at[i, 'Count']
        candidate=pref_profile.at[i, 'rank1']
        votes[candidate] += count
    winners=[]
    for cand in cands:
        if votes[cand]==max(votes.values()):
            winners.append(cand)
    return winners
        

def IRV(pref_profile, cands_to_keep, num_cands):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    cands = cands_to_keep[:]

    while True:
        # Initialize vote counts for this round
        round_votes = {cand: 0 for cand in cands}

        # Count first-choice votes
        remaining_votes = 0  # Track remaining valid votes
        for i in range(len(pref_profile)):
            count = pref_profile.at[i, 'Count']
            for col in rank_columns:
                candidate = pref_profile.at[i, col]
                if candidate in cands:
                    round_votes[candidate] += count
                    remaining_votes += count
                    break

        # Calculate dynamic majority threshold
        threshold = remaining_votes / 2

        # Check for majority
        for cand, votes in round_votes.items():
            if votes > threshold:
                return [cand]  # Winner

        # Find the candidate(s) with the fewest votes
        min_votes = min(round_votes.values())
        candidates_to_eliminate = [cand for cand, votes in round_votes.items() if votes == min_votes]

        # Randomly eliminate one candidate if there's a tie for fewest votes
        candidate_to_eliminate = random.choice(candidates_to_eliminate)
        cands.remove(candidate_to_eliminate)

        # If only one candidate remains, they are the winner
        if len(cands) == 1:
            return cands  # Winner by default

import pandas as pd

def plurality_runoff(pref_profile, cands_to_keep, num_cands):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    cands = cands_to_keep[:]
    votes = {cand: 0 for cand in cands}

    # Count first-choice votes
    for i in range(len(pref_profile)):
        count = pref_profile.at[i, 'Count']
        candidate = pref_profile.at[i, 'rank1']
        votes[candidate] += count

    # Get the top two candidates
    sorted_candidates = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    top_two_cands = [cand for cand, _ in sorted_candidates[:2]]

    # Runoff between the top two candidates
    runoff_votes = {cand: 0 for cand in top_two_cands}
    for i in range(len(pref_profile)):
        for t in range(1, len(cands) + 1):
            candidate = pref_profile.at[i, f'rank{t}']
            if candidate in top_two_cands:
                runoff_votes[candidate] += pref_profile.at[i, 'Count']
                break

    # Determine the winner in the runoff
    winner = max(runoff_votes, key=runoff_votes.get)
    return [winner]
            
def Condorcet_winner(pref_profile, cands_to_keep, num_cands, shortcut,pairwise_matrix):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    # Shortcut: Restrict to top 5 candidates by plurality scores
    if shortcut and len(cands_to_keep) > 5:
        plurality_scores = {cand: 0 for cand in cands_to_keep}
        for k in range(len(pref_profile)):
            plurality_scores[pref_profile.at[k, 'rank1']] += pref_profile.at[k, 'Count']

        # Get the top 5 candidates by plurality score
        top_candidates = sorted(plurality_scores, key=plurality_scores.get, reverse=True)[:5]
    else:
        top_candidates = cands_to_keep

    #pairwise_matrix=pairwise_comparisons_matrix(pref_profile, cands_to_keep,num_cands,shortcut)

    # Determine if there is a Condorcet winner
    for cand in top_candidates:
        if all(pairwise_matrix[cand][opponent] > pairwise_matrix[opponent][cand] for opponent in top_candidates if opponent != cand):
            return [cand]  # Condorcet winner found

    return False  # No Condorcet winner


def Weak_Condorcet_winner(pref_profile, cands_to_keep, num_cands, shortcut):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    # Shortcut: Restrict to top 5 candidates by plurality scores
    if shortcut and len(cands_to_keep) > 5:
        plurality_scores = {cand: 0 for cand in cands_to_keep}
        for k in range(len(pref_profile)):
            plurality_scores[pref_profile.at[k, 'rank1']] += pref_profile.at[k, 'Count']

        # Get the top 5 candidates by plurality score
        top_candidates = sorted(plurality_scores, key=plurality_scores.get, reverse=True)[:5]
    else:
        top_candidates = cands_to_keep

    rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]

    # Initialize a pairwise comparison matrix
    pairwise_matrix = {cand: {opponent: 0 for opponent in top_candidates if opponent != cand} for cand in top_candidates}

    # Perform pairwise comparisons
    for _, row in pref_profile.iterrows():
        count = row['Count']
        for cand in top_candidates:
            for opponent in top_candidates:
                if cand != opponent:
                    # Find the rank of each candidate
                    rank_cand = next((rank for rank, c in enumerate(row[rank_columns], start=1) if c == cand), float('inf'))
                    rank_opponent = next((rank for rank, c in enumerate(row[rank_columns], start=1) if c == opponent), float('inf'))

                    # Increment pairwise count if one candidate is ranked higher
                    if rank_cand < rank_opponent:
                        pairwise_matrix[cand][opponent] += count

    # Find all weak Condorcet winners
    weak_winners = []
    for cand in top_candidates:
        # A weak Condorcet winner doesn't lose any matchup
        if all(pairwise_matrix[cand][opponent] >= pairwise_matrix[opponent][cand] for opponent in top_candidates if opponent != cand):
            weak_winners.append(cand)

    return weak_winners if weak_winners!=[] else False


def minimax_winner(pref_profile, cands_to_keep, num_cands, shortcut, pairwise_matrix):
    
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile
    # Check for a Condorcet winner
    condorcet_winner = None
    for cand in cands_to_keep:
        is_winner = True
        for opponent in cands_to_keep:
            if cand != opponent and pairwise_matrix[cand][opponent] <= pairwise_matrix[opponent][cand]:
                is_winner = False
                break
        if is_winner:
            condorcet_winner = cand
            break

    # If a Condorcet winner is found, return them
    if condorcet_winner:
        return [condorcet_winner]

    # Otherwise, calculate the maximum defeat margin for each candidate
    max_defeat_margin = {cand: 0 for cand in cands_to_keep}
    for cand in cands_to_keep:
        for opponent in cands_to_keep:
            if cand != opponent:
                defeat_margin = pairwise_matrix[opponent][cand] - pairwise_matrix[cand][opponent]
                if defeat_margin > max_defeat_margin[cand]:
                    max_defeat_margin[cand] = defeat_margin

    # Find the smallest maximum defeat margin
    min_max_defeat = min(max_defeat_margin.values())

    # Find all candidates with this minimum maximum defeat margin (there could be ties)
    winners = [cand for cand, margin in max_defeat_margin.items() if margin == min_max_defeat]

    return winners

from itertools import combinations

def is_smith_set(pairwise_matrix, candidates, subset):
    """
    Helper function to check if a given subset of candidates is a valid Smith set.
    It checks if no candidate in the subset is defeated by any candidate outside the subset.
    """
    for cand in subset:
        for opponent in candidates:
            if opponent != cand and opponent not in subset:
                if pairwise_matrix[opponent][cand] > pairwise_matrix[cand][opponent]:
                    return False
    return True

#Crude function, assumes Smith set has size less than 6, otherwise returns False
def Smith_set(pref_profile, cands_to_keep, num_cands, shortcut, pairwise_matrix):
    if len(cands_to_keep) < num_cands:
        all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
        updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

        new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
        new_profile['Count'] = pref_profile['Count']
        pref_profile = new_profile

    # Shortcut: Restrict to top 5 candidates by plurality scores
    if shortcut and len(cands_to_keep) > 5:
        plurality_scores = {cand: 0 for cand in cands_to_keep}
        for k in range(len(pref_profile)):
            plurality_scores[pref_profile.at[k, 'rank1']] += pref_profile.at[k, 'Count']

        # Get the top 5 candidates by plurality score
        top_candidates = sorted(plurality_scores, key=plurality_scores.get, reverse=True)[:5]
    else:
        top_candidates = cands_to_keep

    # Check for Smith set of size 1 (i.e. Condorcet winner)
    #I'm assuming this was already done.
    """
    for cand in top_candidates:
        if is_smith_set(pairwise_matrix, top_candidates, [cand]):
            return [cand]
    """
    # Check for Smith set of size 2-5
    for j in range(1,6):
        sets=combinations(top_candidates, j)
        for subset in sets:
            if is_smith_set(pairwise_matrix, top_candidates, subset):
                return list(subset)

    # No valid Smith set found up to size 5
    return False
    

