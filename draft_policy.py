import copy
import math
import random
from typing import Optional

from team import Team
from data import Data
from mcts import MCTS


class Policy:
    _policies = ["mcts", "offline", "random", "highest_available", "epsilon_highest_available", "epsilon_offline"]

    def __init__(
            self,
            policy: str,
            epsilon: Optional[float] = 0.2,
            random_seed: Optional[int] = None,
            offline_policy: Optional[dict] = None,
    ):
        if random_seed is not None:
            random.seed(random_seed)
        assert policy in self._policies
        self.policy = policy
        self.epsilon = epsilon
        self.offline_policy = None
        self.mcts = None
        self.random_seed = random_seed

    def get_action(
            self,
            team: Team,
            current_round: Optional[int] = None,
            data: Optional[Data] = None,
            teams: Optional[list[Team]] = None,
            policies: Optional[list] = None,
    ):
        if self.policy == "offline":
            return self._offline_policy_action(team, current_round)
        if self.policy == "random":
            return self._random_action(team)
        if self.policy == "highest_available":
            return self._highest_available_action(team, data)
        if self.policy == "epsilon_highest_available":
            return self._epsilon_highest_available_action(team, data)
        if self.policy == "epsilon_offline":
            return self._epsilon_offline_policy_action(team, current_round)
        if self.policy == "mcts":
            if self.mcts is None:
                self.mcts = MCTS(random_seed=self.random_seed)
            return self.mcts.get_action(
                team=team,
                data=data,
                teams=teams,
                policies=policies,
                current_round=current_round,
            )

    def update_learned_policy(self, draft_results: dict) -> None:
        if self.offline_policy is None:
            self.offline_policy = {i: dict() for i in range(1, len(draft_results["position_draft_order"]) + 1)}
        for _round, position in enumerate(draft_results["position_draft_order"], 1):
            self.offline_policy[_round][position] = (self.offline_policy[_round].get(position, 0) +
                                                     int(draft_results["score"]))

    def _epsilon_highest_available_action(self, team: Team, data: Data) -> str:
        rand = random.random()
        if rand > self.epsilon:
            return self._highest_available_action(team, data)

        return self._random_action(team)

    def _epsilon_offline_policy_action(self, team: Team, current_round: int):
        if random.random() > self.epsilon:
            return self._offline_policy_action(team, current_round)

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

    def _offline_policy_action(self, team: Team, current_round: int) -> str:
        if self.offline_policy is None:
            return self._random_action(team)

        positions_left = list(team.needed_pos_counts.keys())
        best_option = None
        best_option_value = -math.inf
        _offline_policy = self.offline_policy.get(current_round, {})
        for position in _offline_policy:
            if _offline_policy[position] > best_option_value and position in positions_left:
                best_option = position
                best_option_value = _offline_policy[position]

        if best_option is None:
            best_option = self._random_action(team)

        return best_option

    @staticmethod
    def _random_action(team: Team) -> str:
        _positions_needed = []
        for pos, needed in team.needed_pos_counts.items():
            _positions_needed += [pos] * needed

        return random.choice(_positions_needed)

    def get_offline_policy(self, pos_counts: dict) -> list:
        _offline_policy = []
        _fake_team = Team(pos_counts)
        for rnd in self.offline_policy:
            _action = self._offline_policy_action(team=_fake_team, current_round=rnd)
            _fake_team.add_player(_action, 0)
            _offline_policy.append(_action)

        return _offline_policy
