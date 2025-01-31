from fractions import Fraction
import os
import csv
import pandas as pd
from pandas.errors import EmptyDataError, DataError
import pathlib
from typing import Optional

from votekit.pref_profile import PreferenceProfile
from votekit.ballot import Ballot
from votekit.elections import STV
from votekit.cleaning import remove_noncands

def new_loader(   
    ##converts our csv files to PreferenceProfiles to be used directly in votekit
    fpa: str,
    seats_col: Optional[int] = None, ##index of numseats column. could be -1 or -2 or None based on our formatting
    id_col: Optional[int] = None, ##index of voterid column  
    #rank_cols: list[int] = [],
    weight_col: Optional[int] = None,
 
):
    df = pd.read_csv(
        fpa,
        on_bad_lines="error",
        encoding="utf8",
        index_col=False,
        delimiter=None,
    )
    if not os.path.isfile(fpa):
        raise FileNotFoundError(f"File with path {fpa} cannot be found")

    fpa = pathlib.Path(fpa)

    if df.empty:
        raise EmptyDataError("Dataset cannot be empty")
#    if id_col is not None and df.iloc[:, id_col].isnull().values.any():  # type: ignore
#        raise ValueError(f"Missing value(s) in column at index {id_col}")
#    if id_col is not None and not df.iloc[:, id_col].is_unique:
#        raise DataError(f"Duplicate value(s) in column at index {id_col}")

    ranks = list(x for x in df.columns if str(x)[:4] == "rank")
    num_seats = 1

    if seats_col:
        num_seats = df.iloc[0,seats_col] ##might need to change based on the num seats column 
    
    df = df.loc[:,ranks]
    grouped = df.groupby(ranks, dropna=False)
    ballots = []

    for group, group_df in grouped:
        ranking = tuple(
            [frozenset({None}) if pd.isnull(c) else frozenset({str(c)}) for c in group]
        )
        voter_set = None
        if id_col is not None:
            voter_set = set(str(group_df.iloc[:, id_col]))
        weight = len(group_df)
        if weight_col is not None:
            weight = sum(group_df.iloc[:, weight_col])
        b = Ballot(ranking=ranking, weight=Fraction(weight), voter_set=voter_set)
        ballots.append(b)
    return (PreferenceProfile(ballots=tuple(ballots)), num_seats)


    