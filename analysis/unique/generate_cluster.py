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

num_of_samples = 2015 #2015 is the number of samples. change this is data is different. this helps create percentage values.

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
        matrix[method_to_idx[methods[i]], method_to_idx[methods[i]]] = num_of_samples
            
matrix /= num_of_samples
matrix = np.log1p(matrix)  
similarity_matrix = cosine_similarity(matrix.T)
plt.figure(figsize=(10, 8))
sns.heatmap(matrix, xticklabels=all_methods, yticklabels=all_methods, cmap='coolwarm', annot=True)
plt.title("Similarity Between Voting Methods")
plt.show()

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
