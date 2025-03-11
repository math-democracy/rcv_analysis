
import json
from itertools import combinations
from collections import Counter

file_path = './all.json'

# Load the JSON file
with open(file_path, "r") as file:
    data = json.load(file)

# Pairwise analysis
pairwise_counter = Counter()
for top_level_key in data.values():  # Iterate over top-level keys
    for location in top_level_key.values():
        print(location)
        for person_methods in location.values():
            pairs = combinations(sorted(set(person_methods)), 2)  # Get unique pairs
            pairwise_counter.update(pairs)

sorted_pairs = sorted(pairwise_counter.items(), key=lambda x: x[1], reverse=True)


group_counter = Counter()
for top_level_key in data.values():  # Iterate over top-level keys
    for location in top_level_key.values():
        for person_methods in location.values():
            group = tuple(sorted(set(person_methods)))
            group_counter[group] += 1

group_pairs = sorted(group_counter.items(), key=lambda x: x[1], reverse=True)


print(sorted_pairs)
json_data = [
    {"methods": list(keys), "elections": value} for keys, value in sorted_pairs
]

# Write to a JSON file
with open("analysis.json", "w") as json_file:
    json.dump(json_data, json_file, indent=4)



# print("\nPairwise Analysis:")
# for pair, count in sorted_pairs:
#     print(f"{pair}: {count}")

# print("\nGrouped Analysis:")
# for pair, count in group_pairs:
#     print(f"{pair}: {count}")