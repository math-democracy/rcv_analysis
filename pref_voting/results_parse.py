import pandas as pd
import json

data_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/australian_results.csv'
results_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/unique.json'

def read_data(data_file):
    data = pd.read_csv(data_file, header=None)
    data.columns = data.iloc[0]
    data = data.drop(0).reset_index(drop=True)
    return data

def find_not_unanimous_results(data):
    results = {}
    for index, row in data.iterrows():
        file_name = row[0]
        result = {}
        for col_index, value in row[1:].items():
            if value:
                if value not in result:
                    result[value] = []
                result[value].append(col_index)
        if len(result) > 1:
            results[f'{file_name}'] = result
    print(len(results))
    return results

def export_data(res):
    with open(results_file, 'w') as json_file:
        json.dump(res, json_file, indent=4)

data = read_data(data_file)
results = find_not_unanimous_results(data)

