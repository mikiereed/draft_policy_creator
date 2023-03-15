import copy
import math
import random

from data import Data
from draft import Draft
from draft_policy import Policy
from mcts import MCTS


def print_policies(policies: list[Policy], pos_counts: dict) -> None:
    for idx in range(len(policies)):
        print(f"{idx}: {policies[idx].get_offline_policy(pos_counts)}")


def simulate_n_drafts(policies: list[Policy], pos_counts: dict, data: Data, n: int, update_offline: bool = False):
    wins_by_index = [0] * team_count
    for sim_number in range(n):
        draft = Draft(pos_counts, policies)
        _data = copy.deepcopy(data)
        draft.simulate(_data)
        results = draft.results()
        if update_offline:
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

    return wins_by_index


def offline_policy_testing(n_draft_data: int, pos_counts: dict, team_count: int, random_seed_start: int = None) -> list:
    random_seed = random_seed_start if random_seed_start is not None else random.randint(1, 1_000_000)

    policy_improvement_average = [0] * team_count
    for i in range(n_draft_data):
        print(f"data set {i} ===================================================================")
        data = Data(team_count, pos_counts, percent_extra=0, random_seed=random_seed)

        # test random policies only
        policies = [Policy(policy="random", random_seed=random_seed) for _ in range(team_count)]
        random_wins_count = simulate_n_drafts(policies=policies, pos_counts=pos_counts, data=data, n=10_000,
                                              update_offline=True)
        print({i: random_wins_count[i] for i in range(len(random_wins_count))})

        # test offline policy
        for j in range(len(policies)):
            _policies = copy.deepcopy(policies)
            _policies[j].policy = "offline"
            policy_wins_count = simulate_n_drafts(policies=_policies, pos_counts=pos_counts, data=data, n=10_000)
            print(f"offline for {j}")
            print(f"{j}: {policies[j].get_offline_policy(pos_counts)}")
            random_policy_wins = random_wins_count[j]
            offline_policy_wins = policy_wins_count[j]
            print(f"random wins: {random_policy_wins} / offline policy wins: {offline_policy_wins}")
            policy_improvement = int(((offline_policy_wins - random_policy_wins) / random_policy_wins) * 100)
            policy_improvement_average[j] += (1 / (i + 1)) * (policy_improvement - policy_improvement_average[j])
            print(f"policy improvement: {policy_improvement}%")
            print("-----------------------------------------------------")

        random_seed += 1

    return policy_improvement_average


def offline_epsilon_policy_testing(n_draft_data: int, pos_counts: dict, team_count: int, random_seed_start: int = None) -> list:
    random_seed = random_seed_start if random_seed_start is not None else random.randint(1, 1_000_000)

    policy_improvement_average = [0] * team_count
    for i in range(n_draft_data):
        print(f"data set {i} ===================================================================")
        data = Data(team_count, pos_counts, percent_extra=0, random_seed=random_seed)

        # test random policies only
        policies = [Policy(policy="random", random_seed=random_seed) for _ in range(team_count)]
        random_wins_count = simulate_n_drafts(policies=policies, pos_counts=pos_counts, data=data, n=10_000,
                                              update_offline=False)
        print(f"random win counts ===========================")
        print({i: random_wins_count[i] for i in range(len(random_wins_count))})

        # train offline vs each other
        policies = [Policy(policy="epsilon_offline", random_seed=random_seed) for _ in range(team_count)]
        offline_training_wins_count = simulate_n_drafts(policies=policies, pos_counts=pos_counts, data=data, n=10_000,
                                              update_offline=True)
        print(f"offline win counts ===========================")
        print({i: offline_training_wins_count[i] for i in range(len(offline_training_wins_count))})

        # test offline policy
        for policy in policies:
            policy.policy = "random"
        for j in range(len(policies)):
            _policies = copy.deepcopy(policies)
            _policies[j].policy = "offline"
            policy_wins_count = simulate_n_drafts(policies=_policies, pos_counts=pos_counts, data=data, n=10_000)
            print(f"offline for {j}")
            print(f"{j}: {policies[j].get_offline_policy(pos_counts)}")
            random_policy_wins = random_wins_count[j]
            offline_policy_wins = policy_wins_count[j]
            print(f"random wins: {random_policy_wins} / offline policy wins: {offline_policy_wins}")
            policy_improvement = int(((offline_policy_wins - random_policy_wins) / random_policy_wins) * 100)
            policy_improvement_average[j] += (1 / (i + 1)) * (policy_improvement - policy_improvement_average[j])
            print(f"policy improvement: {policy_improvement}%")
            print("-----------------------------------------------------")

        random_seed += 1

    return policy_improvement_average


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
    #
    # policy_improvement_average = offline_policy_testing(n_draft_data=100, pos_counts=pos_counts, team_count=team_count, random_seed_start=88)
    # print({i: f'{int(policy_improvement_average[i])}%' for i in range(len(policy_improvement_average))})

    # policy_improvement_average = offline_epsilon_policy_testing(n_draft_data=100, pos_counts=pos_counts, team_count=team_count, random_seed_start=None)
    # print({i: f'{int(policy_improvement_average[i])}%' for i in range(len(policy_improvement_average))})

    monte_carlo_tree_search = MCTS(c=math.sqrt(2))
    random_seed = 1
    # make function to run this n times

    policies = [Policy(policy="mcts", random_seed=random_seed) for _ in range(team_count)]
    draft = Draft(needed_pos_and_counts=pos_counts, policies=policies)
    data = Data(team_count=team_count, pos_counts=pos_counts)
    # policy_improvement_average = monte_carlo_tree_search.get_action(draft.current_team_index, data=data, teams=draft.teams)
    draft.simulate(data)
