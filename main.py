import copy

from data import Data
from draft import Draft
from draft_policy import Policy


if __name__ == "__main__":
    team_count = 10
    pos_counts = {
        "qb": 1,
        "rb": 2,
        "wr": 3,
        "te": 1,
        "k": 1,
        "dst": 1,
    }

    data = Data(team_count, pos_counts, percent_extra=50, random_seed=None)
    policy = Policy(epsilon=0.2)
    for _ in range(100):
        draft = Draft(team_count, pos_counts)
        _data = copy.deepcopy(data)
        draft.simulate(_data, policy)
        policy.update_learned_policy(draft.results())
    print(draft)
