import pandas as pd
import json
from collections import Counter

# file_path = '/Users/belle/Desktop/build/rcv_proposal/david_methods/processed_results/australia_results.csv'

# df = pd.read_csv(file_path)

# file,numCands,irv,plurality,plurality_runoff,borda_pm,borda_om_no_uwi,borda_avg_no_uwi,borda_trunc_points_scheme,condorcet,minimax,smith_set
# file,plurality,plurality_with_runoff_put,instant_runoff_for_truncated_linear_orders,bottom_two_runoff_instant_runoff_put,instant_runoff_put,borda_for_profile_with_ties,condorcet,minimax,top_cycle

method_mapping = {
    "irv": "instant_runoff_put",
    "plurality": "plurality",
    "plurality_runoff": "plurality_with_runoff_put",
    "borda_pm": "borda_for_profile_with_ties",
    "borda_om_no_uwi": "borda_for_profile_with_ties",
    "borda_avg_no_uwi": "borda_for_profile_with_ties",
    "borda_trunc_points_scheme": "borda_for_profile_with_ties",
    "condorcet": "condorcet",
    "minimax": "minimax",
    "smith_set": "top_cycle",
}

df1 = pd.read_csv('/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/scottish_results.csv')
df2 = pd.read_csv('/Users/belle/Desktop/build/rcv_proposal/david_methods/processed_results/scotland_results.csv')

print(df1)
print(df2)
# Ensure the file column is consistent for joining
df1['file'] = df1['file'].str.strip()
df2['file'] = df2['file'].str.strip() #for american: str.replace('processed_data/', '', regex=False)

merged_df = pd.merge(df1, df2, on='file', suffixes=('_file1', '_file2'))

print(merged_df)
comparison_results = []

count = Counter()
for _, row in merged_df.iterrows():
    file_path = row["file"]
    result = {"file": file_path, "matches": {}}

    for method1, method2 in method_mapping.items():
        result1 = row.get(f"{method1}_file1", "[]")
        result2 = row.get(f"{method2}_file2", "[]")

        if isinstance(result1, str):
            result1 = eval(result1) if result1.startswith('[') else [result1]
        if isinstance(result2, str):
            result2 = eval(result2) if result2.startswith('[') else [result2]
        

        if result1 == result2:
            result["matches"][method1] = result1 == result2
        else:
            result["matches"][method1] = f'{result1}; {result2}'
            count[method1] += 1
    
    comparison_results.append(result)

print(count)
results_df = pd.DataFrame(comparison_results)

results_df.to_json('comparison_results.json', orient='records', indent=4)

print("Comparison completed. Results saved to 'comparison_results.csv' and 'comparison_results.json'.")

with open('comparison_results.json', "r") as f:
    data = json.load(f)

filtered_data = [
    entry for entry in data
    if any(value is not True for value in entry["matches"].values())
]

with open('difference_comparison_results.json', "w") as f:
    json.dump(filtered_data, f, indent=4)

print(f"Filtered results saved to difference_comparison_results")

