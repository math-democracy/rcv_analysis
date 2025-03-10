import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("sorted_by_elections.csv") 

df = df[df['country'] == 'civs']
df = df[df['method'] == 'borda']

df['percentage'] = pd.to_numeric(df['percentage'], errors='coerce')

method_columns = ["IRV", "approval", "borda-avg", "borda-om", "borda-pm", "bucklin", 
                  "condorcet", "minimax", "plurality", "ranked-pairs", "smith", 
                  "smith-minimax", "smith_irv", "smith_plurality", "top-3-truncation", "top-two"]

method_counts = df.groupby("percentage")[method_columns].sum()

plt.figure(figsize=(12, 6))
for method in method_columns:
    plt.plot(method_counts.index, method_counts[method], marker='o', label=method)

plt.xlabel("Percentage")
plt.ylabel("Number of Elections")
plt.title("Fringe Winners")
plt.legend(title="Method", bbox_to_anchor=(1.05, 1), loc='upper left')  # Move legend outside
plt.grid(True)

plt.show()
