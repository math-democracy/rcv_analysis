import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

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
    df = pd.read_csv("./results.csv")

    invalid_counts = {
        "one_two": str((df["one_two"] == -1).sum()),
        "one_something": str((df["one_something"] == -1).sum())
    }

    df = df[df["one_two"] != -1]

    stats = df.describe().to_dict()

    rounded_stats = {col: {k: round(v, 4) for k, v in stat.items()} for col, stat in stats.items()}

    output = {
    "stats": rounded_stats,
    "invalid_counts": invalid_counts
    }
    
    with open("distribution.json", "w") as f:
        json.dump(output, f, indent=2)

create_graph()