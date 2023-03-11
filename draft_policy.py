import math
import random

from team import Team
from data import Data


class Policy:
    policies = ["learned", "random", "highest_available", "epsilon_highest_available", "epsilon_learned"]
    learned_policy = None

    def __init__(self, epsilon):
        self._epsilon = epsilon

    def get_action(self, team: Team, current_round: int, data: Data):
        if team.policy == "learned":
            return self._learned_policy_action(team, current_round)
        if team.policy == "random":
            return self._random_action(team)
        if team.policy == "highest_available":
            return self._highest_available_action(team, data)
        if team.policy == "epsilon_highest_available":
            return self._epsilon_highest_available_action(team, data)
        if team.policy == "epsilon_learned":
            return self._epsilon_learned_policy_action(team, current_round)

    @staticmethod
    def update_learned_policy(draft_results: dict) -> None:
        if Policy.learned_policy is None:
            Policy.learned_policy = {i: dict() for i in range(1, len(draft_results[0]["position_draft_order"]) + 1)}
        for team in draft_results:
            for _round, position in enumerate(draft_results[team]["position_draft_order"], 1):
                Policy.learned_policy[_round][position] = Policy.learned_policy[_round].get(position, 0) + draft_results[team]["score"]

    def _epsilon_highest_available_action(self, team: Team, data: Data) -> str:
        if random.random() > self._epsilon:
            return self._highest_available_action(team, data)

        return self._random_action(team)

    def _epsilon_learned_policy_action(self, team: Team, current_round: int):
        if random.random() > self._epsilon:
            return self._learned_policy_action(team, current_round)

        return self._random_action(team)

    @staticmethod
    def _highest_available_action(team: Team, data: Data):
        max_score = 0
        max_position = ""
        for position in team.needed_pos_counts.keys():
            if data.players[position][0] > max_score:
                max_score = data.players[position][0]
                max_position = position

        return max_position

    @staticmethod
    def _learned_policy_action(team: Team, current_round: int) -> str:
        if Policy.learned_policy is None:
            return Policy._random_action(team)

        positions_left = list(team.needed_pos_counts.keys())
        best_option = positions_left[0]
        for position in positions_left:
            if (Policy.learned_policy[current_round].get(position, 0) >
                    Policy.learned_policy[current_round].get(best_option, math.inf)):
                best_option = position

        return best_option

    @staticmethod
    def _random_action(team) -> str:
        return random.choice(list(team.needed_pos_counts.keys()))
