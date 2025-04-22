import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import ast

def create_graph():
    df = pd.read_csv("./results.csv")
    plt.figure(figsize=(10, 6))
    sns.kdeplot(df["one_two"], label="one_two", shade=True)
    sns.kdeplot(df["one_something"], label="one_something", shade=True)
    plt.title("Distribution of percentage votes to candidate of the same party")
    plt.xlabel("Value")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def generate_statistics():
    df = pd.read_csv("/Users/belle/Desktop/build/rcv/analysis/party_linkage/results6.csv")
    print(df)
    # df['rank_obj'] = df['rank_obj'].apply(ast.literal_eval)
    # rank_df = pd.json_normalize(df['rank_obj'])

    # Combine with original df if needed
    # df_combined = pd.concat([df.drop(columns='rank_obj'), rank_df], axis=1)

    # invalid_counts = {
    #     # "one_two": str((df["one_two"] == -1).sum()),
    #     "one_change": str((df["one_change"] == -1).sum())
    # }

    # df = df[df["one_two"] != -1]
    df = df[df["one_change"] != -1]

    stats = df.describe().to_dict()

    # rank_states = rank_df.describe().to_dict()

    rounded_stats = {col: {k: round(v, 4) for k, v in stat.items()} for col, stat in stats.items()}

    output = {
    "stats": rounded_stats,
    # "invalid_counts": invalid_counts,
    # "rank": rank_states
    }
    
    with open("distribution2.json", "w") as f:
        json.dump(output, f, indent=2)

def plot_rank_mean():
    with open('distribution2.json', 'r') as f:  # Replace with your actual file path
        data = json.load(f)

    # Extract the mean values
    rank_stats = data['rank']
    ranks = [rank for rank in rank_stats.keys() if rank != "rank1"]
    means = [rank_stats[rank]['mean'] for rank in ranks]

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(ranks, means, marker='o', linestyle='-', color='steelblue')
    plt.title('Percentage of second party vote at each rank')
    plt.xlabel('Rank')
    plt.ylabel('Mean Percentage')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

generate_statistics()