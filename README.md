# rcv_proposal 

### Research Questions:
* For each election, do the methods of Borda, Condorcet, IRV, Bucklin, etc., choose the same winner? If not, why not? Does a method tend to choose a more centrist or fringe candidate?
* What does ``fringe'' mean?
* For each election and each method, check for the spoiler effect.
* Are there methods which disincentivize movement toward the center in some sense? Do these finding hold true if we vary voter turnout?
* Beef up Atkinson et al. study using CES data. Incorporate things like voters not showing up if there isn't a candidate close enough to them.
* Check IRV for monotonicity and no-show failures.
* For each method, how often does the method select the candidate with the third or fewest first-place votes? We study this because voters might not like such an outcome.
* Minimax is probably the simplest Condorcet method. In three-candidate elections the method has no fairness criterion weaknesses I know of. Check how often in the 4-candidate case the method might select the Condorcet loser.
* For each method, how safe is it for a voter to rank their favorite candidate first?
* Analysis of top3, top4, top5 methods. Does the Condorcet winner make it through to the runoff round? Do any noticeably undeserving candidates make it to the runoff round? Are there monotonicity/strategic issues regarding the runoff round? Susceptibility to spoiler effect?
* For everything above, use models from VoteKit to generate synthetic elections and rerun analysis.
* Administrative challenges for various methods?
* Look at later-no-harm criterion for Condorcet methods.
