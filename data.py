import math
from numpy import random
from scipy.stats import skewnorm
from typing import Optional

# crudely based on 2022 stat distribution
POS_MEAN_AND_STD = {
    "QB": {"MEAN": 280, "STD": 30},
    "RB": {"MEAN": 140, "STD": 60},
    "WR": {"MEAN": 130, "STD": 45},
    "TE": {"MEAN": 80, "STD": 35},
    "DST": {"MEAN": 180, "STD": 20},
    "K": {"MEAN": 180, "STD": 5},
}


class Data:
    def __init__(self, team_count: int, pos_counts: dict, percent_extra: int = 0, random_seed: Optional[int] = None):
        if random_seed is not None:
            random.seed(random_seed)
        players = dict()
        for pos in pos_counts:
            pos_mean = POS_MEAN_AND_STD[pos.upper()]["MEAN"]
            pos_std = POS_MEAN_AND_STD[pos.upper()]["STD"]
            scores = skewnorm.rvs(
                a=pos_std,
                loc=pos_mean/2,
                scale=pos_std,
                size=math.ceil(pos_counts[pos] * team_count * (1 + (percent_extra / 100)))
            )
            players[pos] = sorted(scores, reverse=True)

        self.players = players

    def get_and_remove_score(self, pos: str, player: int = 0) -> float:
        score = self.players[pos][player]
        del self.players[pos][player]

        return score

    def data_to_csv(self):
        ...  # TODO
