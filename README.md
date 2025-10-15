# Empirical Analysis of RCV

This is the repository for some of the code to analyze ranked choice voting in real world elections in America, Scotland, and Australia. More data can be found here: https://mathematics-democracy-institute.org/empirical-analysis-of-ranked-choice-voting-methods/

The raw winner results from each election can be found in [current](./results/current).

## [Uniqueness](./analysis/unique)
We compare the various voting methods to determine how often the elect the same winner. This allows us to create a “similarity matrix” which we can then use to create heatmaps and dendrograms to visualize the “closeness” of the voting methodologies. Results are shown for each of American, Australia, and Scotland, as well as across all three countries.

First [generate a dictionary](./analysis/unique/count_unique.py) to group, for each election, methods that elect the same winner. Then, run a [pairwise comparison](./analysis/unique/pairwise_comparison.py) and generate the [graphs](./analysis/unique/generate_cluster.py).

## [Fringe winners](./analysis/fringe)
One hopes that an election method will avoid electing “fringe” candidates. Unfortunately there isn't consensus on what makes a candidate fringe. In our case, we labeled a candidate “fringe” based on their (average) Borda score in comparison to the maximum (average) Borda score. We counted fringe winners for each of 9 ways of setting a “fringe threshold” and displayed those results in a graph.

## [First Place Rank](./analysis/first_place_analysis)
American voters are used to the winner being the candidate with the number of first place votes, so it might be concerning for voters if the winning candidate is “too far” from being a winning candidate under plurality. These graphs show the number of elections where the winning candidate was not the plurality winner or plurality runner-up.

## [Top 4 stability](./analysis/stability/)
Top-k voting methods --- where one voting method is used to winnow down the candidate pool, and a second is used to select the winner --- have some appeal in voting reform circles. We determined the number of elections where the winner would change if you reduced the candidate pool to the top four plurality winners. Note that Scotland has a large number of such elections since their elections are actually multi-winner, and so a single party will often be represented by a number of candidates on the ballot (and, therefore, voters aligned with that party might have ballots that rank those candidates differently).

## [Majority winner](./analysis/majority_fav/)/[Condorcet Loser](./analysis/condorcet_loser/)
Majority winner: when a majority winner exists, the method does not elect the majority winner. Condorcet loser: the method elects a condorcet loser (candidate that is defeated in a head to head compairson with every other candidate). These graphs show the number of elections where a particular method was susceptible to these failures.

## [Cloning](./analysis/candidate_cloning/)
A “clone” candidate is one which aligns with a leading candidate in many ways; in plurality elections, a competing party might try to incentivize such a clone candidate to run in the hopes of ciphoning off support from the original candidate. We simulated the insertion of one clone candidate in elections, giving the clone candidate a probability (either 0%, 10%, 20%, 30%, 40%, or 50%) of appearing ahead of the original candidate on the ballot. We then checked to see whether the insertion of this clone candidate would spoil the election (i.e., change the result of the election). These graphs show the proportion of elections which were spoiled in this way.

Run [run cloned elections](./analysis/candidate_cloning/cloning.py) then [merge the files](./analysis/candidate_cloning/merge_cloning_files.py). Next, [extract the interesting cases of a spoiler effect](./analysis/candidate_cloning/compare.py) and [create graphs](./analysis/candidate_cloning/graph.py).

## [Spoiler](./analysis/spoiler/)
A candidate is called a “spoiler” if they are a losing candidate, but their removal from the pool of candidates results in a different winner in the election. In these graphs we determined the number of elections in which at least one spoiler candidate existed.

There is a side investigation into when spoiler candidates are fringe candidates that can be found within [this folder](./analysis/spoiler/spoiler_vs_fringe/). 

_small note: to import main meethods into each file, you'll need to import sys and use sys.append to the folder where main methods is_