import pandas as pd

df = pd.read_csv("/Users/belle/Desktop/build/rcv_proposal/analysis/fringe/sorted_by_elections.csv")

df.fillna(0, inplace=True)

method_columns = df.columns[5:]  

df[method_columns] = df[method_columns].apply(pd.to_numeric, errors='coerce').fillna(0)

result = df.groupby("country")[method_columns].sum()
result = result.loc[result.sum(axis=1).sort_values(ascending=False).index]

result.to_json("output.json", orient="index")

print(result)