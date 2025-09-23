"""generate spoiler graph for keep_first results"""
import matplotlib.pyplot as plt
import json 
import matplotlib.cm as cm

def run():
    data = {
            "borda-om": 211,
            "plurality": 144,
            "bucklin": 94,
            "top-3-truncation": 92,
            "top-two": 67,
            "borda-avg": 65,
            "borda-pm": 56,
            "IRV": 44,
            "smith-minimax": 5,
            "smith_plurality": 5,
            "condorcet": 5,
            "approval": 5,
            "smith_irv": 5,
            "ranked-pairs": 5,
            "minimax": 5,
            "smith": 4
        }

    del data["approval"]

    print(data)

    methods, counts = zip(*sorted(data.items(), key=lambda x: x[1], reverse=True))

    plt.figure(figsize=(10, 6))
    plt.barh(methods, counts, color="skyblue")
    plt.xlabel("Number of elections")
    plt.ylabel("Method")
    plt.title("Number of condensed scottish elections where a method is susceptible to spoiler effect")
    plt.gca().invert_yaxis()  
    plt.savefig('analysis/mimic_single_party/methods/first_last_mentioned/keep_first/scotland_condensed_keep_first_spoiler.png')

run()