import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
with open("analysis.json", "r") as file:  
    data = json.load(file)

G = nx.Graph()

for entry in data:
    methods = entry["methods"]
    elections = entry["elections"]
    
    if len(methods) == 2: 
        method1, method2 = methods
        G.add_edge(method1, method2, weight=elections)

plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G, seed=42)  

edges = G.edges(data=True)
weights = [d["weight"] for (_, _, d) in edges]  # Extract edge weights for thickness
nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", width=[w/500 for w in weights], font_size=10, font_weight="bold")

plt.title("Similarity Between Voting Methods")
plt.show()