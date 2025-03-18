import json
import ast

methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval']
files = {}

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
        return f"['{party}']"
    else:
        return candidate

def get_comparisons(filepath):
    method_counts = dict.fromkeys(methods,0)
    multi_winner_removed = dict.fromkeys(methods,0)
    someone_else_from_party_wins = dict.fromkeys(methods,0)

    with open(filepath) as file:
        comparison = json.load(file)

    changes = comparison['changes']

    for file in changes.keys():
        file_metadata = changes[file]
        method_changes = file_metadata['changes']

        removed_candidates = file_metadata['removed_candidates']
        removed_parties = set()
        for r in removed_candidates:
            removed_parties.add(get_party(r))
        removed_parties = list(removed_parties)

        for m in method_changes.keys():
            #print(method_changes[m]['multi_party_winner'])
            cand_removed = False
            if method_changes[m]['multi_party_winner'] != '[]' and ast.literal_eval(method_changes[m]['multi_party_winner'])[0] in removed_candidates:
                multi_winner_removed[m] += 1
                cand_removed = True

            if get_party(method_changes[m]['single_party_winner']) in removed_parties:
                method_counts[m] += 1

                if file not in files:
                    files[file] = {}

                if cand_removed:
                    someone_else_from_party_wins[m] += 1

                files[file]['scores'] = file_metadata['scores']
                files[file]['removed'] = file_metadata['removed_candidates']
                files[file][m] = method_changes[m]
                
    method_counts_pct = {}
    someone_else_from_party_wins_pct = {}
    for m in method_counts:
        method_counts_pct[m] = round(method_counts[m] / comparison['metadata']['method_counts'][m],3)
        if multi_winner_removed[m] != 0:
            someone_else_from_party_wins_pct[m] = round(someone_else_from_party_wins[m] / multi_winner_removed[m], 3)
        else:
            someone_else_from_party_wins_pct[m] = None

    all_data = {'original_single_v_multi_metadata': comparison['metadata'],
                'new_winner_from_removed_multi_party': method_counts,
                'new_winner_from_removed_multi_party_pct': method_counts_pct,
                'multi_winner_removed': multi_winner_removed,
                'multi_winner_removed_party_still_wins': someone_else_from_party_wins,
                'multi_winner_removed_party_still_wins_pct': someone_else_from_party_wins_pct,
                'files': files}
    return all_data


def main():
    METHOD = 'mention_score'
    filepath = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/{METHOD}/single_v_multi_comparison.json'
    output_data = get_comparisons(filepath)

    # write to output file
    output_file = filepath[:-30] + 'removed_party_metadata.json'
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")


if __name__ == '__main__':
    main()