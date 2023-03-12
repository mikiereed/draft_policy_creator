import copy

from data import Data
from draft import Draft
from draft_policy import Policy


def print_policies(policies: list[Policy], pos_counts: dict) -> None:
    for idx in range(len(policies)):
        print(f"{idx}: {policies[idx].get_offline_policy(pos_counts)}")


def simulate_n_drafts(policies: list[Policy], pos_counts: dict, data: Data, n: int):
    wins_by_index = [0] * team_count
    for sim_number in range(n):
        draft = Draft(pos_counts, policies)
        _data = copy.deepcopy(data)
        draft.simulate(_data)
        results = draft.results()
        for i in range(len(policies)):
            policies[i].update_learned_policy(results[i])
        for best in results:
            wins_by_index[best] += 1
            break

        # if sim_number % (n * 0.5) == 0:
        #     print(f"simulation {sim_number}")
            # print_policies(policies, pos_counts)
            # print("----------------------------------------------")

    # print_policies(policies, pos_counts)
    # print()
    print({i: wins_by_index[i] for i in range(len(wins_by_index))})


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
    random_seed = None

    data = Data(team_count, pos_counts, percent_extra=0, random_seed=random_seed)

    # test random policies only
    policies = [Policy(policy="random", random_seed=random_seed) for _ in range(team_count)]
    simulate_n_drafts(policies=policies, pos_counts=pos_counts, data=data, n=10_000)

    # test offline policy
    for i in range(len(policies)):
        print(f"offline for {i}")
        _policies = copy.deepcopy(policies)
        _policies[i].policy = "offline"
        simulate_n_drafts(policies=_policies, pos_counts=pos_counts, data=data, n=10_000)
        print(f"{i}: {policies[i].get_offline_policy(pos_counts)}")
        print("-----------------------------------------------------")
