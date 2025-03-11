import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.metrics.pairwise import cosine_similarity
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import SpectralClustering
from sklearn.cluster import AffinityPropagation
import networkx as nx

with open('analysis.json', 'r') as f:
    data = json.load(f)

all_methods = sorted(set(m for entry in data for m in entry["methods"]))
method_to_idx = {m: i for i, m in enumerate(all_methods)}

matrix = np.zeros((len(all_methods), len(all_methods)))
### FOR PAIRWISE COMPARISON
for entry in data:
    methods = entry["methods"]
    elections = entry["elections"]
    
    # For each pair of methods in the entry, increment the co-occurrence matrix
    for i in range(len(methods)):
        for j in range(i + 1, len(methods)):
            idx_i = method_to_idx[methods[i]]
            idx_j = method_to_idx[methods[j]]
            matrix[idx_i, idx_j] += elections
            matrix[idx_j, idx_i] += elections  # Since it's symmetric

    for i in range(len(methods)):
        matrix[method_to_idx[methods[i]], method_to_idx[methods[i]]] = 2015
            
matrix /= 2015
# matrix = np.log1p(matrix)  
# similarity_matrix = cosine_similarity(matrix.T)
# plt.figure(figsize=(10, 8))
# sns.heatmap(matrix, xticklabels=all_methods, yticklabels=all_methods, cmap='coolwarm', annot=True)
# plt.title("Similarity Between Voting Methods")
# plt.show()

#### FOR GROUP COMPARISON
# matrix = np.zeros((len(all_methods), len(all_methods)))
# for entry in data:
#     methods = entry["methods"]
#     elections = entry["elections"]
#     indices = [method_to_idx[m] for m in methods]
#     for i in indices:
#         for j in indices:
#             matrix[i, j] += elections

# print(matrix)

#### For denodogram
distance_matrix = 1 - (matrix / np.max(matrix))  
np.fill_diagonal(distance_matrix, 0)
condensed_dist = squareform(distance_matrix) 

linkage = sch.linkage(condensed_dist, method='ward')

# # Plot dendrogram
plt.figure(figsize=(12, 6))
sch.dendrogram(linkage, labels=all_methods, leaf_rotation=90, leaf_font_size=10)
plt.title("Hierarchical Clustering of Voting Methods")
plt.xlabel("Voting Methods")
plt.ylabel("Distance")
plt.show()

sc = SpectralClustering(n_clusters=2, affinity='precomputed')
# labels = sc.fit_predict(matrix)
ap = AffinityPropagation(affinity='precomputed')
labels = ap.fit_predict(matrix)

sorted_indices = np.argsort(labels)
sorted_matrix = matrix[np.ix_(sorted_indices, sorted_indices)]

sns.heatmap(sorted_matrix, cmap="coolwarm", xticklabels=sorted_indices, yticklabels=sorted_indices)
plt.title("Clustered Similarity Matrix")
plt.show()


G = nx.Graph()

for i in range(len(matrix)):
    G.add_node(i, cluster=labels[i])

for i in range(len(matrix)):
    for j in range(i + 1, len(matrix)):
        if matrix[i, j] > 0.3:  
            G.add_edge(i, j, weight=matrix[i, j])

pos = nx.spring_layout(G) 
nx.draw(G, pos, with_labels=True, node_color=labels, cmap=plt.cm.Set1, node_size=500)
plt.title("Spectral Clustering Graph")
plt.show()
