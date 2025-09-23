import pandas as pd
import math
import matplotlib.pyplot as plt

def gen_metadata(full_path):
    df = pd.read_csv(full_path)
    methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']

    data = {}

    for m in methods:
        value_counts = df[f"{m}_rank"].value_counts(dropna=False).to_dict()
        cleaned_counts = {}
        for k, v in value_counts.items():
            if k != "multiple" and not (isinstance(k, float) and math.isnan(k)):
                cleaned_counts[str(int(k))] = v
            else:
                cleaned_counts[str(k)] = v

        sorted_counts = dict(sorted(cleaned_counts.items()))
        data[m] = sorted_counts

    gen_graph(data, full_path.replace('/new/','/graphs/').replace('.csv','.png'))


def gen_graph(method_counts, output_file):
    methods = list(method_counts.keys())
    num_methods = len(methods)

    # --- FIGURE SETUP ---
    cols = 4  # number of subplot columns
    rows = math.ceil(num_methods / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3), constrained_layout=True)
    axes = axes.flatten()  # Flatten in case it's a 2D array

    # --- PLOT EACH METHOD ---
    for i, method in enumerate(methods):
        ax = axes[i]
        counts = method_counts[method]
        keys = list(counts.keys())
        values = list(counts.values())

        ax.bar(keys, values, color="steelblue", edgecolor="black")
        ax.set_title(method, fontsize=16)
        ax.set_xlabel("Rank", fontsize=12)
        ax.set_ylabel("Count", fontsize=12)
        ax.tick_params(axis='x', rotation=45, labelsize=12)
        ax.tick_params(axis='y', labelsize=12)

    # Hide any unused subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # --- SAVE FIGURE ---
    plt.suptitle("Distribution of First-Place Vote Rankings for Winners", fontsize=18)
    plt.savefig(output_file, dpi=300)
    plt.close()

    print(f"Saved panel plot to: {output_file}")

if __name__ == '__main__':
    countries = ['america','australia','scotland','civs']

    for c in countries:
        gen_metadata(f"analysis/first_place_analysis/new/{c}.csv")