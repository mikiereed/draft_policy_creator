import copy
import math
import random

from data import Data
from draft import Draft
from draft_policy import Policy


def print_policies(policies: list[Policy], pos_counts: dict) -> None:
    for idx in range(len(policies)):
        print(f"{idx}: {policies[idx].get_offline_policy(pos_counts)}")


def simulate_n_drafts(policies: list[Policy], pos_counts: dict, data: Data, n: int, update_offline: bool = False,
                      verbose: bool = False):
    wins_by_index = [0] * team_count
    for sim_number in range(n):
        draft = Draft(needed_pos_and_counts=pos_counts, policies=policies)
        _data = copy.deepcopy(data)
        draft.simulate(_data)
        results = draft.results()
        if update_offline:
            for i in range(len(policies)):
                policies[i].update_learned_policy(results[i])
        for best in results:
            wins_by_index[best] += 1
            if verbose:
                print(f"{best}", end=", ")
            break

    if verbose:
        print()

    return wins_by_index


def policy_testing(
        policy_to_test: str,
        opponent_policies: str,
        n_draft_data: int,
        simulations_per_data: int,
        pos_counts: dict,
        team_count: int,
        random_seed_start: int = None,
) -> list:
    random_seed = random_seed_start if random_seed_start is not None else random.randint(1, 1_000_000)
    update_offline = False
    if policy_to_test == "offline" or opponent_policies == "offline":
        update_offline = True

    policy_statistics = [{"baseline_wins": 0, "policy_wins": 0} for _ in range(team_count)]
    for i in range(n_draft_data):
        print(f"data set {i} ===================================================================")
        data = Data(team_count, pos_counts, percent_extra=0, random_seed=random_seed)

        # test opponent policies only for baseline
        policies = [Policy(policy=opponent_policies, random_seed=random_seed) for _ in range(team_count)]
        baseline_wins_count = simulate_n_drafts(policies=policies,
                                                pos_counts=pos_counts,
                                                data=data,
                                                n=simulations_per_data,
                                                update_offline=update_offline,
                                                )
        print({j: baseline_wins_count[j] for j in range(len(baseline_wins_count))})
        for j in range(team_count):
            policy_statistics[j]["baseline_wins"] += baseline_wins_count[j]

        # train offline if testing offline
        if update_offline:
            simulate_n_drafts(policies=policies,
                              pos_counts=pos_counts,
                              data=data,
                              n=10_000,
                              update_offline=update_offline,
                              )

        # test policy
        for j in range(len(policies)):
            print(f"{policy_to_test} for {j}")
            _policies = copy.deepcopy(policies)
            _policies[j].policy = policy_to_test
            verbose = False
            if policy_to_test == "mcts":
                verbose = True
            policy_wins_count = simulate_n_drafts(policies=_policies,
                                                  pos_counts=pos_counts,
                                                  data=data,
                                                  n=simulations_per_data,
                                                  verbose=verbose
                                                  )
            # if policy_to_test == "offline":
            #     print(f"{j}: {policies[j].get_offline_policy(pos_counts)}")
            random_policy_wins = baseline_wins_count[j]
            policy_wins = policy_wins_count[j]
            policy_statistics[j]["policy_wins"] += policy_wins
            print(f"random wins: {random_policy_wins} / {policy_to_test} policy wins: {policy_wins}")
            if random_policy_wins:
                policy_improvement = int(((policy_wins - random_policy_wins) / random_policy_wins) * 100)
            else:
                policy_improvement = math.inf
            print(f"policy improvement: {policy_improvement}%")
            print("-----------------------------------------------------")

        random_seed += 1

    for j in range(team_count):
        if policy_statistics[j]["baseline_wins"] != 0:  # divide by zero error
            policy_statistics[j]["policy_improvement"] = int(((policy_statistics[j]["policy_wins"] -
                                                               policy_statistics[j]["baseline_wins"]) /
                                                              policy_statistics[j]["baseline_wins"]) * 100)
        else:
            policy_statistics[j]["policy_improvement"] = math.inf

    return policy_statistics


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
    random_seed_start = 88
    n_draft_data = 40
    n_drafts = 25

    # offline policy testing
    print(f"offline ============================================================")
    offline_policy_improvement_average = policy_testing(policy_to_test="offline",
                                                        opponent_policies="random",
                                                        n_draft_data=n_draft_data,
                                                        simulations_per_data=n_drafts,
                                                        pos_counts=pos_counts,
                                                        team_count=team_count,
                                                        random_seed_start=random_seed_start,
                                                        )
    print("============================================================")
    print("RESULTS FOR OFFLINE============================================================")
    for i in range(team_count):
        print(f'{i}: {offline_policy_improvement_average[i]["policy_improvement"]}%')
        print(f'random: {offline_policy_improvement_average[i]["baseline_wins"]} | offline: {offline_policy_improvement_average[i]["policy_wins"]}')
        print("============================================================")

    # mcts policy testing
    print(f"mcts ============================================================")
    mcts_policy_improvement_average = policy_testing(policy_to_test="mcts",
                                                     opponent_policies="random",
                                                     n_draft_data=n_draft_data,
                                                     simulations_per_data=n_drafts,
                                                     pos_counts=pos_counts,
                                                     team_count=team_count,
                                                     random_seed_start=random_seed_start,
                                                     )
    print("============================================================")
    print("RESULTS FOR MCTS============================================================")
    for i in range(team_count):
        print(f'{i}: {mcts_policy_improvement_average[i]["policy_improvement"]}%')
        print(
            f'random: {mcts_policy_improvement_average[i]["baseline_wins"]} | mcts: {mcts_policy_improvement_average[i]["policy_wins"]}')
        print("============================================================")
    print("RESULTS FOR ALL============================================================")
    for i in range(team_count):
        print(f'{i}= offline: {offline_policy_improvement_average[i]["policy_improvement"]}% | mcts: {mcts_policy_improvement_average[i]["policy_improvement"]}%')
        print(
            f'random: {offline_policy_improvement_average[i]["baseline_wins"]} | offline: {offline_policy_improvement_average[i]["policy_wins"]} | mcts: {mcts_policy_improvement_average[i]["policy_wins"]}')
        print("============================================================")
