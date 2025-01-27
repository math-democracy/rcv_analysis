import pandas as pd
import json

data_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/scottish_results.csv'
results_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/unique2.json'


# file,numCands,irv,plurality,plurality_runoff,borda_pm,borda_om_no_uwi,borda_avg_no_uwi,borda_trunc_points_scheme,condorcet,minimax,smith_set
# file,plurality,plurality_with_runoff_put,instant_runoff_for_truncated_linear_orders,bottom_two_runoff_instant_runoff_put,instant_runoff_put,borda_for_profile_with_ties,condorcet,minimax,top_cycle

def read_data(data_file):
    data = pd.read_csv(data_file, header=None)
    data.columns = data.iloc[0]
    data = data.drop(0).reset_index(drop=True)
    # data = data.drop(columns=['numCands'])
    data = data[['file', 'plurality','plurality_with_runoff_put','instant_runoff_for_truncated_linear_orders','bottom_two_runoff_instant_runoff_put','instant_runoff_put','borda_for_profile_with_ties','condorcet','minimax','top_cycle']]
    return data

def find_not_unanimous_results(data):
    count = 0
    results = {}
    for index, row in data.iterrows():
        if 'Skipped' not in row.values and 'ERROR' not in row.values and 'NULL' not in row.values and 'Write-in' not in row.values:
            count += 1
            file_name = row[0]
            result = {}
            for col_index, value in row[1:].items():
                if value:
                    if value not in result:
                        result[value] = []
                    result[value].append(col_index)
            if len(result) > 1:
                results[f'{file_name}'] = result
    print(count)
    print(len(results))
    return results

def export_data(res):
    with open(results_file, 'w') as json_file:
        json.dump(res, json_file, indent=4)

data = read_data(data_file)
results = find_not_unanimous_results(data)
export_data(results)
