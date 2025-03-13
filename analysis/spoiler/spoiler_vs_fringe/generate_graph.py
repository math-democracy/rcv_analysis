import matplotlib.pyplot as plt
import json 
import matplotlib.cm as cm

with open(f'./new_results/america_svf_metadata.json') as file:
    data = json.load(file)

data = data["fringe_count"]

x_values = sorted([float(key.split("_")[-1]) for key in data.keys()])

methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']

y_values = {method: [] for method in methods}

for key in sorted(data.keys(), key=lambda k: float(k.split("_")[-1])):
    for method in methods:
        y_values[method].append(data[key].get(method, 0)) 

cmap = cm.get_cmap("tab20", len(methods))
method_colors = {method: cmap(i) for i, method in enumerate(methods)}

plt.figure(figsize=(10, 6))
for method, y_vals in y_values.items():
    plt.plot(x_values, y_vals, marker="o", linestyle="-", label=method, color=method_colors[method])

plt.xlabel("Fringe Threshold Percentage (Borda)")
plt.ylabel("Number of Elections")
plt.title("America Elections w/ Fringe Spoiler Candidate")
plt.legend(title="Method", bbox_to_anchor=(1.05, 1), loc='upper left')  # Move legend outside
plt.grid(True)
plt.tight_layout()

plt.show()