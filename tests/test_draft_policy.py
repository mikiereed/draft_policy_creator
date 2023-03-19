import random

from draft_policy import Policy
from team import Team
from data import Data

pos_and_counts_needed = {
    "QB": 1,
    "RB": 2,
    "WR": 3,
}
data = Data(10, pos_and_counts_needed, random_seed=1)


def test_init():
    policy = Policy(policy="random", epsilon=0.3, random_seed=5)

    assert policy.policy == "random"
    assert policy.epsilon == 0.3
    assert policy.offline_policy is None


def test_get_action_random():
    policy = Policy("random", random_seed=3)

    team = Team(pos_and_counts_needed)
    random_action = policy.get_action(team=team)

    assert random_action == "RB"

    random_action = policy.get_action(team=team)

    assert random_action == "WR"


def test_get_action_high_avail():
    policy = Policy("highest_available", random_seed=3)
    team = Team(pos_and_counts_needed)
    highest_available_action = policy.get_action(
        team=team,
        current_round=1,
        data=data
    )

    assert highest_available_action == "QB"


def test_get_action_episilon_high():
    policy = Policy("epsilon_highest_available", epsilon=0.9, random_seed=1)
    team = Team(pos_and_counts_needed)
    epsilon_highest_available_action = policy.get_action(
        team=team,
        data=data
    )

    assert epsilon_highest_available_action == "QB"

    epsilon_highest_available_action = policy.get_action(
        team=team,
        data=data
    )

    assert epsilon_highest_available_action == "WR"
