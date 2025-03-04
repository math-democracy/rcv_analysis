import pandas as pd

def merge(file1, file2, output):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    merged = pd.merge(df1, df2, on=['file', 'candidate_cloned', 'numCands'], how='inner')

    merged.to_csv(output)

for country in ['america', 'australia', 'scotland']:
    for percentage in ['0.1', '0.2', '0.3', '0.4', '0.5']:
        merge(f'/Users/belle/Desktop/build/rcv_proposal/analysis/candidate_cloning/results1/{country}_{percentage}.csv', f'/Users/belle/Desktop/build/rcv_proposal/analysis/candidate_cloning/results2/{country}_{percentage}.csv', f'/Users/belle/Desktop/build/rcv_proposal/analysis/candidate_cloning/results/{country}_{percentage}.csv')