import pandas as pd
import json
import os

def load_and_compare(folder_path):
    dataframes = []

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if filename.endswith('.csv'):
                filename = filename.replace('.csv', '')
                f = filename.split('_')
                country = f[0]
                if len(f) > 1:
                    percentage = f[1]
                else:
                    percentage = 0

                df = pd.read_csv(full_path)
                df['country'] = country
                df['percentage'] = percentage
                df["file"] = df["file"].apply(lambda x: x[1:] if isinstance(x, str) and x.startswith("/") else x)
                df["file"] = df["file"].str.replace(".csv", "", regex=False)
                df["candidate_cloned"] = df["candidate_cloned"].str.replace(".csv", "", regex=False)

                dataframes.append(df)

                print(filename, country, percentage)

    df1 = pd.read_csv('/Users/belle/Desktop/build/rcv_proposal/results/current/america.csv', usecols=lambda col: col not in ["Unnamed: 0", "smith"])
    df1['country'] = "america"
    df1['percentage'] = "ORIGINAL"
    df1["file"] = df1["file"].apply(lambda x: x[1:] if isinstance(x, str) and x.startswith("/") else x)
    df1["file"] = df1["file"].str.replace(".csv", "", regex=False)


    df2 = pd.read_csv('/Users/belle/Desktop/build/rcv_proposal/results/current/australia.csv', usecols=lambda col: col not in ["Unnamed: 0", "smith"])
    df2['country'] = "australia"
    df2['percentage'] = "ORIGINAL"
    df2["file"] = df2["file"].apply(lambda x: x[1:] if isinstance(x, str) and x.startswith("/") else x)
    df2["file"] = df2["file"].str.replace(".csv", "", regex=False)


    df3 = pd.read_csv('/Users/belle/Desktop/build/rcv_proposal/results/current/scotland.csv', usecols=lambda col: col not in ["Unnamed: 0", "smith"])
    df3['country'] = "scotland"
    df3['percentage'] = "ORIGINAL"
    df3["file"] = df3["file"].apply(lambda x: x[1:] if isinstance(x, str) and x.startswith("/") else x)
    df3["file"] = df3["file"].str.replace(".csv", "", regex=False)

    dataframes.append(df1)
    dataframes.append(df2)
    dataframes.append(df3)

    master_df = pd.concat(dataframes, ignore_index=True)
    master_df.to_csv('updated_results.csv')


load_and_compare('/Users/belle/Desktop/build/rcv_proposal/analysis/candidate_cloning/results_hpc/2')