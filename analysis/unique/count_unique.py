import pandas as pd
import json

data_file = '' #election results data file
results_file = '' #output file

def read_data(data_file):
    data = pd.read_csv(data_file, header=None)
    data.columns = data.iloc[0]
    data = data.drop(0).reset_index(drop=True)
    print(len(data))
    # for analyzing w/ david's data: data = data.drop(columns=['numCands'])
    data = data[['file','plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']]
    return data

# group the results so winners are the keys and methods that elected the winner are in an array as the value
def find_not_unanimous_results(data):
    count = 0
    results = {}
    for _, row in data.iterrows():
        if 'Skipped' not in row.values and 'ERROR' not in row.values and 'NULL' not in row.values and 'Write-in' not in row.values:
            count += 1
            file_name = row[0]
            result = {}
            for col_index, value in row[1:].items():
                if value:
                    if value not in result:
                        result[value] = []
                    result[value].append(col_index)
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
